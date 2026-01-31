import typer
from pathlib import Path
from typing import Optional
import asyncio

app = typer.Typer()

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
            typer.echo(f"✓ Found {len(changes)} specification changes")

            for change in changes[:5]:  # Show first 5
                typer.echo(
                    f"  - {change.change_type.value}: "
                    f"{change.provider}/{change.resource_type} "
                    f"(v{change.api_version})"
                )

            if len(changes) > 5:
                typer.echo(f"  ... and {len(changes) - 5} more")

            if auto_generate:
                typer.echo("\n🔄 Generating code updates...")
                # Trigger code generation
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

        typer.echo(f"\n📊 Mazure API Coverage Report\n")
        typer.echo(f"Total Azure Providers: {coverage['total_providers']}")
        typer.echo(f"Implemented in Mazure: {coverage['implemented_providers']}")
        typer.echo(f"Coverage: {coverage['coverage_percentage']}%\n")

        typer.echo("✓ Implemented Providers:")
        for provider in coverage['providers']['implemented'][:10]:
            typer.echo(f"  - {provider}")

        typer.echo(f"\n❌ Missing Providers (showing 10 of {len(coverage['providers']['missing'])}):")
        for provider in coverage['providers']['missing'][:10]:
            typer.echo(f"  - {provider}")

    asyncio.run(run())

def _find_spec_path(provider: str, resource_type: str, api_version: str) -> Optional[Path]:
    """Find spec file in default location"""
    specs_root = Path("specs/azure-rest-api-specs/specification")
    if not specs_root.exists():
        return None

    # Search for file named {resource_type}.json
    candidates = list(specs_root.rglob(f"{resource_type}.json"))

    matches = []
    for candidate in candidates:
        parts = candidate.parts
        if api_version in parts:
             provider_short = provider.split('.')[-1].lower()
             if provider in str(candidate) or provider_short in str(candidate).lower():
                 matches.append(candidate)

    if not matches:
        return None

    exact_matches = [m for m in matches if provider in str(m)]
    if exact_matches:
        return exact_matches[0]

    return matches[0]

@app.command()
def generate(
    provider: str = typer.Argument(..., help="Provider namespace"),
    resource_type: str = typer.Argument(..., help="Resource type"),
    api_version: str = typer.Argument(..., help="API version"),
    spec_path: Path = typer.Option(None, help="Path to the spec file")
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

    typer.echo(f"🔄 Generating {provider}/{resource_type} (v{api_version})...")

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
    typer.echo("✓ Service generated successfully")

if __name__ == "__main__":
    app()
