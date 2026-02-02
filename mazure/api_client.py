"""
Mazure Python API Module

This module provides programmatic access to all Mazure CLI commands,
allowing other Python packages to invoke Mazure functionality without
using the CLI.

Example usage:
    from mazure.api_client import MazureAPI

    api = MazureAPI()

    # Generate a service
    api.generate(
        provider="Microsoft.Compute",
        resource_type="virtualMachines",
        api_version="2024-03-01"
    )

    # Start the mock server (non-blocking)
    api.serve(port=5050, host="0.0.0.0", blocking=False)

    # Sync with Azure specs
    changes = api.sync(specs_path="specs/azure-rest-api-specs", auto_generate=False)

    # Get service status
    status = api.status()
"""

import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from threading import Thread
import time


class MazureAPI:
    """
    Programmatic Python API for Mazure commands.

    This class provides methods to invoke all Mazure CLI functionality
    from within Python code.
    """

    def __init__(self, mazure_root: Optional[Path] = None):
        """
        Initialize the Mazure API client.

        Args:
            mazure_root: Optional path to Mazure project root. Defaults to current directory.
        """
        self.mazure_root = mazure_root or Path.cwd()
        self._server_thread = None

    def generate(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        spec_path: Optional[Path] = None
    ) -> None:
        """
        Generate service implementation from OpenAPI specification.

        Args:
            provider: Provider namespace (e.g., "Microsoft.Compute")
            resource_type: Resource type (e.g., "virtualMachines")
            api_version: API version (e.g., "2024-03-01")
            spec_path: Optional path to spec file. Will auto-discover if not provided.

        Raises:
            FileNotFoundError: If spec file not found
            RuntimeError: If generation fails
        """
        from mazure.sync.codegen import MazureCodeGenerator
        from mazure.cli.sync import _find_spec_path

        if spec_path is None:
            spec_path = _find_spec_path(provider, resource_type, api_version)
            if not spec_path:
                raise FileNotFoundError(
                    f"Could not find spec file for {provider}/{resource_type} "
                    f"version {api_version}"
                )

        async def _run():
            generator = MazureCodeGenerator(
                specs_path=spec_path,
                mazure_root=self.mazure_root
            )
            await generator.generate_service(
                provider=provider,
                resource_type=resource_type,
                api_version=api_version,
                spec_path=spec_path
            )

        asyncio.run(_run())

    def serve(
        self,
        port: int = 5050,
        host: str = "0.0.0.0",
        blocking: bool = True,
        debug: bool = False
    ) -> None:
        """
        Start the Mazure mock server.

        Args:
            port: Port to run the server on (default: 5050)
            host: Host to bind to (default: "0.0.0.0")
            blocking: If True, blocks until server stops. If False, runs in background thread.
            debug: Enable Flask debug mode

        Example:
            # Blocking mode (for scripts)
            api.serve(port=5050)

            # Non-blocking mode (for tests or other apps)
            api.serve(port=5050, blocking=False)
            # ... do other work ...
            api.stop_server()
        """
        from mazure.services import app as flask_app
        from mazure.services.utils import services, register

        # Register all available services
        all_services = services(flask_app, [])
        register(flask_app, all_services)

        if blocking:
            flask_app.run(debug=debug, port=port, host=host)
        else:
            # Run in background thread
            def _run_server():
                flask_app.run(debug=debug, port=port, host=host, use_reloader=False)

            self._server_thread = Thread(target=_run_server, daemon=True)
            self._server_thread.start()

            # Give server time to start
            time.sleep(1)

    def stop_server(self) -> None:
        """
        Stop the background server if running in non-blocking mode.

        Note: This relies on the server thread being daemonized,
        so it will stop when the main program exits.
        """
        if self._server_thread and self._server_thread.is_alive():
            # Flask doesn't provide a clean way to stop the server programmatically
            # The daemon thread will be terminated when the main program exits
            pass

    def sync(
        self,
        specs_path: Path = Path("specs/azure-rest-api-specs"),
        auto_generate: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Sync with latest Azure API specifications.

        Args:
            specs_path: Path to azure-rest-api-specs repository
            auto_generate: Automatically generate code for changes

        Returns:
            List of changes detected, each as a dict with keys:
            - change_type: Type of change (ADDED, MODIFIED, etc.)
            - provider: Provider namespace
            - resource_type: Resource type
            - api_version: API version
        """
        from mazure.sync.spec_sync import AzureSpecSyncEngine

        async def _run():
            sync_engine = AzureSpecSyncEngine(
                specs_repo_path=specs_path,
                mazure_root=self.mazure_root
            )
            changes = await sync_engine.sync()

            if auto_generate and changes:
                from mazure.sync.codegen_command import process_pending_tasks
                await process_pending_tasks(
                    tasks_file=sync_engine.tasks_file_path,
                    specs_path=specs_path,
                    mazure_root=self.mazure_root
                )

            return [
                {
                    "change_type": c.change_type.value,
                    "provider": c.provider,
                    "resource_type": c.resource_type,
                    "api_version": c.api_version
                }
                for c in changes
            ]

        return asyncio.run(_run())

    def status(self) -> Dict[str, Any]:
        """
        Get status of generated services and server.

        Returns:
            Dictionary with keys:
            - services: List of generated service names
            - server_running: Boolean indicating if server is running
            - server_url: URL of server if running, None otherwise
        """
        import socket
        import re

        api_dir = self.mazure_root / "mazure" / "api"
        generated = []

        if api_dir.exists():
            for f in api_dir.glob("*.py"):
                if f.name == "__init__.py":
                    continue

                try:
                    content = f.read_text(encoding='utf-8')
                    match = re.search(r'API Routes for (.*)', content)
                    if match:
                        generated.append(match.group(1))
                    else:
                        generated.append(f.stem.replace('_', '.'))
                except Exception:
                    generated.append(f.stem.replace('_', '.'))

        # Check if server is running
        port = 5050
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            is_running = s.connect_ex(('localhost', port)) == 0

        return {
            "services": sorted(generated),
            "server_running": is_running,
            "server_url": f"http://localhost:{port}" if is_running else None
        }

    def list_specs(
        self,
        service: Optional[str] = None,
        provider: Optional[str] = None,
        resource: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List available services, providers, and resources from synced specs.

        Args:
            service: Service name (e.g., "compute")
            provider: Provider namespace (e.g., "Microsoft.Compute")
            resource: Resource type (e.g., "virtualMachines")
            query: Search string for providers and resources

        Returns:
            Dictionary with available items at the requested level
        """
        import re

        specs_root = Path("specs/azure-rest-api-specs/specification")
        if not specs_root.exists():
            raise FileNotFoundError(
                f"Azure specs not found at {specs_root}. "
                "Run 'git clone https://github.com/Azure/azure-rest-api-specs.git "
                "specs/azure-rest-api-specs --depth=1' first."
            )

        if query:
            matches = set()
            for s_dir in specs_root.iterdir():
                if not s_dir.is_dir():
                    continue

                for p_dir in s_dir.rglob("Microsoft.*"):
                    if not p_dir.is_dir():
                        continue

                    provider_name = p_dir.name
                    if query.lower() in provider_name.lower():
                        matches.add(f"Provider: {provider_name} (in {s_dir.name})")

                    for json_file in p_dir.rglob("*.json"):
                        if json_file.name in ["common.json", "types.json"]:
                            continue

                        res_name = json_file.stem
                        if query.lower() in res_name.lower():
                            matches.add(
                                f"Resource: {res_name} (in {s_dir.name}/{provider_name})"
                            )

            return {"matches": sorted(list(matches), key=str.lower)}

        if service is None:
            services = sorted(
                [d.name for d in specs_root.iterdir() if d.is_dir()],
                key=str.lower
            )
            return {"services": services}

        service_path = specs_root / service
        if not service_path.exists():
            matches = [
                d.name for d in specs_root.iterdir()
                if d.is_dir() and service.lower() in d.name.lower()
            ]
            if matches:
                return {"error": f"Service '{service}' not found", "suggestions": matches}
            return {"error": f"Service '{service}' not found"}

        if provider is None:
            providers = set()
            for p in service_path.rglob("Microsoft.*"):
                if p.is_dir():
                    providers.add(p.name)

            if not providers:
                rm_path = service_path / "resource-manager"
                if rm_path.exists():
                    for p in rm_path.iterdir():
                        if p.is_dir():
                            providers.add(p.name)

            return {"providers": sorted(list(providers), key=str.lower)}

        provider_dirs = [d for d in service_path.rglob(provider) if d.is_dir()]
        if not provider_dirs:
            all_providers = set()
            for p in service_path.rglob("Microsoft.*"):
                if p.is_dir():
                    all_providers.add(p.name)

            matches = [p for p in all_providers if provider.lower() in p.lower()]
            if matches:
                return {
                    "error": f"Provider '{provider}' not found in '{service}'",
                    "suggestions": matches
                }
            return {"error": f"Provider '{provider}' not found in '{service}'"}

        resources = {}
        for p_dir in provider_dirs:
            for json_file in p_dir.rglob("*.json"):
                if json_file.name in ["common.json", "types.json"]:
                    continue

                res_name = json_file.stem
                if res_name not in resources:
                    resources[res_name] = set()

                for part in json_file.parts:
                    if re.match(r"\d{4}-\d{2}-\d{2}", part):
                        resources[res_name].add(part)

        if resource is None:
            return {"resources": sorted(resources.keys(), key=str.lower)}

        match_key = next((k for k in resources if k.lower() == resource.lower()), None)
        if match_key:
            return {
                "resource": match_key,
                "versions": sorted(list(resources[match_key]), reverse=True)
            }

        return {"error": f"Resource '{resource}' not found for provider '{provider}'"}

    def coverage(self) -> Dict[str, Any]:
        """
        Get API coverage report.

        Returns:
            Dictionary with coverage statistics:
            - total_providers: Total number of Azure providers
            - implemented_providers: Number implemented in Mazure
            - coverage_percentage: Coverage percentage
            - providers: Dict with 'implemented' and 'missing' lists
        """
        from mazure.sync.spec_sync import AzureSpecSyncEngine

        async def _run():
            sync_engine = AzureSpecSyncEngine(
                specs_repo_path=Path("specs/azure-rest-api-specs"),
                mazure_root=self.mazure_root
            )
            await sync_engine.initialize()
            return await sync_engine.get_service_coverage()

        return asyncio.run(_run())

    def compatibility(
        self,
        specs_path: Path = Path("specs/azure-rest-api-specs")
    ) -> Dict[str, Any]:
        """
        Check API version compatibility.

        Args:
            specs_path: Path to azure-rest-api-specs repository

        Returns:
            Compatibility report dictionary
        """
        from mazure.sync.compatibility import CompatibilityMatrix
        import mazure

        matrix = CompatibilityMatrix()
        mazure_root = Path(mazure.__file__).parent.parent
        matrix.load_from_specs(specs_path, mazure_root)

        return matrix.generate_compatibility_report()

    def scenario(
        self,
        template: str,
        apply: bool = False,
        output: Optional[Path] = None
    ) -> str:
        """
        Generate environment state from template.

        Args:
            template: Template name (e.g., "compliance/cmmc")
            apply: Apply the template directly to the running server
            output: Output path for generated script

        Returns:
            Path to generated script, or success message if applied
        """
        from mazure.scenarios.generator import ScenarioGenerator
        import mazure

        mazure_root = Path(mazure.__file__).parent.parent
        generator = ScenarioGenerator(template, mazure_root)

        if apply:
            generator.apply()
            return "Template applied successfully"
        else:
            out = generator.generate_script(output)
            return str(out)
