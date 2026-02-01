import warnings
# Suppress pkg_resources deprecation warning
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", module="mongomock")

import typer
from pathlib import Path
from typing import Optional
import asyncio
import re

app = typer.Typer()

import socket

@app.command()
def status():
    """Show currently generated service implementations and their routes"""
    api_dir = Path("mazure/api")
    if not api_dir.exists():
        typer.echo("No services generated yet.")
        return

    generated = []
    for f in api_dir.glob("*.py"):
        if f.name == "__init__.py":
            continue
        
        # Read the file to get provider/resource from comments
        try:
            content = f.read_text(encoding='utf-8')
            match = re.search(r'API Routes for (.*)', content)
            if match:
                generated.append(match.group(1))
            else:
                generated.append(f.stem.replace('_', '.'))
        except Exception:
            generated.append(f.stem.replace('_', '.'))
    
    if not generated:
        typer.echo("No services generated yet.")
    else:
        typer.echo("[+] Generated Services:")
        for g in sorted(generated):
            typer.echo(f"  - {g}")
        
        # Check if server is running
        port = 5050
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            is_running = s.connect_ex(('localhost', port)) == 0
        
        status_msg = f"RUNNING at http://localhost:{port}" if is_running else f"NOT RUNNING (Default: http://localhost:{port})"
        typer.echo(f"\n[!] Server Status: {status_msg}")
        
        if is_running:
            typer.echo("\n[i] Usage Details:")
            typer.echo("  - Subscription ID: Any valid UUID (e.g., 00000000-0000-0000-0000-000000000000)")
            typer.echo("  - Tenant ID: Any valid UUID")
            typer.echo("  - Auth: Any bearer token is accepted")
        else:
            typer.echo("\nTo start the server, run: mazure serve")
        
        typer.echo("\nSee README.md for more details on making REST calls.")

@app.command(name="list")
def list_specs(
    service: Optional[str] = typer.Argument(None, help="Service name (e.g., compute)"),
    provider: Optional[str] = typer.Argument(None, help="Provider namespace (e.g., Microsoft.Compute)"),
    resource: Optional[str] = typer.Argument(None, help="Resource type (e.g., virtualMachines)")
):
    """List available services, providers, and resources from synced specs"""
    specs_root = Path("specs/azure-rest-api-specs/specification")
    if not specs_root.exists():
        typer.echo(f"Error: Azure specs not found at {specs_root}")
        typer.echo("Run 'git clone https://github.com/Azure/azure-rest-api-specs.git specs/azure-rest-api-specs --depth=1' first.")
        raise typer.Exit(code=1)

    if service is None:
        typer.echo("[+] Available Services (top-level):")
        services = sorted([d.name for d in specs_root.iterdir() if d.is_dir()])
        for s in services:
            typer.echo(f"  - {s}")
        typer.echo("\nUsage: mazure list <service>")
        return

    service_path = specs_root / service
    if not service_path.exists():
        # Try fuzzy match
        matches = [d.name for d in specs_root.iterdir() if d.is_dir() and service.lower() in d.name.lower()]
        if matches:
            typer.echo(f"Service '{service}' not found. Did you mean:")
            for m in matches:
                typer.echo(f"  - {m}")
        else:
            typer.echo(f"Error: Service '{service}' not found.")
        return

    if provider is None:
        typer.echo(f"[+] Providers in '{service}':")
        providers = set()
        for p in service_path.rglob("Microsoft.*"):
            if p.is_dir():
                providers.add(p.name)
        
        if not providers:
            # Some specs don't follow the Microsoft.* naming in dir structure
            # Let's look for any leaf-ish directory under resource-manager
            rm_path = service_path / "resource-manager"
            if rm_path.exists():
                for p in rm_path.iterdir():
                    if p.is_dir():
                        providers.add(p.name)

        for p in sorted(list(providers)):
            typer.echo(f"  - {p}")
        typer.echo(f"\nUsage: mazure list {service} <provider>")
        return

    # Providers can be deeply nested or at multiple locations
    provider_dirs = [d for d in service_path.rglob(provider) if d.is_dir()]
    if not provider_dirs:
        # Try fuzzy match for provider
        all_providers = set()
        for p in service_path.rglob("Microsoft.*"):
             if p.is_dir(): all_providers.add(p.name)
        
        matches = [p for p in all_providers if provider.lower() in p.lower()]
        if matches:
            typer.echo(f"Provider '{provider}' not found in '{service}'. Did you mean:")
            for m in matches:
                typer.echo(f"  - {m}")
        else:
            typer.echo(f"Error: Provider '{provider}' not found in '{service}'.")
        return

    resources = {}
    for p_dir in provider_dirs:
        for json_file in p_dir.rglob("*.json"):
            # Exclude common non-spec files
            if json_file.name in ["common.json", "types.json"]:
                continue
            
            res_name = json_file.stem
            if res_name not in resources:
                resources[res_name] = set()
            
            # Find version pattern YYYY-MM-DD
            for part in json_file.parts:
                if re.match(r"\d{4}-\d{2}-\d{2}", part):
                    resources[res_name].add(part)

    if resource is None:
        typer.echo(f"[+] Resources for provider '{provider}':")
        for res in sorted(resources.keys()):
            typer.echo(f"  - {res}")
        typer.echo(f"\nUsage: mazure list {service} {provider} <resource>")
    else:
        # Check for case-insensitive match
        match_key = next((k for k in resources if k.lower() == resource.lower()), None)
        if match_key:
            typer.echo(f"[+] Available versions for '{match_key}':")
            for ver in sorted(list(resources[match_key]), reverse=True):
                typer.echo(f"  - {ver}")
            typer.echo(f"\nTo generate this service, run:")
            typer.echo(f"mazure generate {provider} {match_key} {sorted(list(resources[match_key]), reverse=True)[0]}")
        else:
            typer.echo(f"Error: Resource '{resource}' not found for provider '{provider}'.")


@app.command()
def sync(
    specs_path: Path = typer.Option(
        "specs/azure-rest-api-specs",
        help="Path to azure-rest-api-specs repository"
    ),
    auto_generate: bool = typer.Option(
        False,
        help="Automatically generate code for changes"
    )
):
    """Sync with latest Azure API specifications"""

    from mazure.sync.spec_sync import AzureSpecSyncEngine

    async def run():
        sync_engine = AzureSpecSyncEngine(
            specs_repo_path=specs_path,
            mazure_root=Path.cwd()
        )

        changes = await sync_engine.sync()

        if changes:
            typer.echo(f"[*] Found {len(changes)} specification changes")

            for change in changes[:5]:  # Show first 5
                typer.echo(
                    f"  - {change.change_type.value}: "
                    f"{change.provider}/{change.resource_type} "
                    f"(v{change.api_version})"
                )

            if len(changes) > 5:
                typer.echo(f"  ... and {len(changes) - 5} more")

            if auto_generate:
                typer.echo("\n[sync] Generating code updates...")
                from mazure.sync.codegen_command import process_pending_tasks
                await process_pending_tasks(
                    tasks_file=sync_engine.tasks_file_path,
                    specs_path=specs_path,
                    mazure_root=Path.cwd()
                )
        else:
            typer.echo("✓ No changes detected")

    asyncio.run(run())

@app.command()
def coverage():
    """Show API coverage report"""

    from mazure.sync.spec_sync import AzureSpecSyncEngine

    async def run():
        sync_engine = AzureSpecSyncEngine(
            specs_repo_path=Path("specs/azure-rest-api-specs"),
            mazure_root=Path.cwd()
        )

        await sync_engine.initialize()
        coverage = await sync_engine.get_service_coverage()

        typer.echo(f"\n[REPORT] Mazure API Coverage Report\n")
        typer.echo(f"Total Azure Providers: {coverage['total_providers']}")
        typer.echo(f"Implemented in Mazure: {coverage['implemented_providers']}")
        typer.echo(f"Coverage: {coverage['coverage_percentage']}%\n")

        typer.echo("[+] Implemented Providers:")
        for provider in coverage['providers']['implemented'][:10]:
            typer.echo(f"  - {provider}")

        typer.echo(f"\n❌ Missing Providers (showing 10 of {len(coverage['providers']['missing'])}):")
        for provider in coverage['providers']['missing'][:10]:
            typer.echo(f"  - {provider}")

    asyncio.run(run())

def _find_spec_path(provider: str, resource_type: str, api_version: str) -> Optional[Path]:
    """Find spec file in default location with optimized search"""
    specs_root = Path("specs/azure-rest-api-specs/specification")
    if not specs_root.exists():
        return None

    # Try both singular and plural versions of the resource type
    variations = [resource_type]
    if resource_type.endswith('s'):
        variations.append(resource_type[:-1])
    else:
        variations.append(resource_type + 's')

    # Optimization: Search specifically in the provider's likely directory
    provider_part = provider.split('.')[-1].lower()
    
    search_dirs = []
    for d in specs_root.iterdir():
        if d.is_dir() and (provider_part in d.name.lower() or d.name.lower() in provider_part):
            search_dirs.append(d)
    
    if not search_dirs:
        search_dirs = [specs_root]

    for search_dir in search_dirs:
        for rt in variations:
            candidates = list(search_dir.rglob(f"{rt}.json"))
            
            matches = []
            for candidate in candidates:
                parts = candidate.parts
                if api_version in parts:
                    if provider in str(candidate) or provider_part in str(candidate).lower():
                        matches.append(candidate)

            if matches:
                exact_matches = [m for m in matches if provider in str(m)]
                if exact_matches:
                    return exact_matches[0]
                return matches[0]

    return None

@app.command()
def generate(
    provider: str = typer.Argument(..., help="Provider namespace"),
    resource_type: str = typer.Argument(..., help="Resource type"),
    api_version: str = typer.Argument(..., help="API version"),
    spec_path: Optional[Path] = typer.Option(None, help="Path to the spec file"),
):
    """Generate service implementation from specification"""
    from mazure.sync.codegen import MazureCodeGenerator

    if spec_path is None:
        typer.echo("Searching for spec file...")
        spec_path = _find_spec_path(provider, resource_type, api_version)
        if not spec_path:
            typer.echo(f"Error: Could not find spec file for {provider}/{resource_type} version {api_version}")
            raise typer.Exit(code=1)
        typer.echo(f"Found spec file: {spec_path}")

    typer.echo(f"[gen] Generating {provider}/{resource_type} (v{api_version})...")

    async def run():
        generator = MazureCodeGenerator(
            specs_path=spec_path, # Not really used in init but passed to generate methods
            mazure_root=Path.cwd()
        )

        await generator.generate_service(
            provider=provider,
            resource_type=resource_type,
            api_version=api_version,
            spec_path=spec_path
        )

    asyncio.run(run())
    typer.echo("[+] Service generated successfully")

@app.command()
def scenario(
    template: str = typer.Argument(..., help="Template name to generate environment from (e.g. compliance/cmmc)"),
    apply: bool = typer.Option(False, help="Apply the template directly to the running server"),
    output: Optional[Path] = typer.Option(None, help="Output path for generated script")
):
    """Generate environment state from template"""
    from mazure.scenarios.generator import ScenarioGenerator
    import mazure

    mazure_root = Path(mazure.__file__).parent.parent
    try:
        generator = ScenarioGenerator(template, mazure_root)

        if apply:
            generator.apply()
            typer.echo("[+] Template applied successfully")
        else:
            out = generator.generate_script(output)
            typer.echo(f"[+] Script generated at: {out}")

    except Exception as e:
        typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)

@app.command()
def compatibility(
    specs_path: Path = typer.Option(
        "specs/azure-rest-api-specs",
        help="Path to azure-rest-api-specs repository"
    ),
    output: Optional[Path] = typer.Option(
        None,
        help="Output report to JSON file"
    )
):
    """Check API version compatibility"""

    from mazure.sync.compatibility import CompatibilityMatrix
    import json
    import mazure

    matrix = CompatibilityMatrix()
    typer.echo("Loading compatibility data...")

    # Resolve package root dynamically to ensure services are found
    # regardless of CWD or installation method
    mazure_root = Path(mazure.__file__).parent.parent
    matrix.load_from_specs(specs_path, mazure_root)

    report = matrix.generate_compatibility_report()

    typer.echo(f"\n[REPORT] Compatibility Report\n")
    typer.echo(f"Total Resource Types: {report['total_resource_types']}")

    for provider, data in report['coverage_by_provider'].items():
        if data['supported'] > 0:
            typer.echo(f"- {provider}: {data['coverage_percentage']}% ({data['supported']}/{data['total']})")

    if report['deprecated_versions']:
        typer.echo(f"\n[!] Found {len(report['deprecated_versions'])} supported deprecated versions")

    if output:
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        typer.echo(f"\nReport saved to {output}")

@app.command()
def serve(
    port: int = typer.Option(5050, help="Port to run the server on"),
    host: str = typer.Option("0.0.0.0", help="Host to run the server on")
):
    """Start the Mazure mock server"""
    from mazure.services import app as flask_app
    from mazure.services.utils import services, register
    
    # Register all available services (passing empty list to services() gets all supported)
    all_services = services(flask_app, [])
    register(flask_app, all_services)
    
    typer.echo(f"[serve] Starting Mazure mock server on {host}:{port}...")
    flask_app.run(
        debug=True,
        port=port,
        host=host
    )

if __name__ == "__main__":
    app()
