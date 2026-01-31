# mazure/sync/codegen.py
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class MazureCodeGenerator:
    """
    Generates Mazure service implementations from Azure OpenAPI specs
    Uses AutoRest for parsing, custom templates for generation
    """

    def __init__(
        self,
        specs_path: Path,
        mazure_root: Path,
        templates_path: Optional[Path] = None
    ):
        self.specs_path = specs_path
        self.mazure_root = mazure_root
        # Adjusted path: assumes mazure_root is repo root
        self.templates_path = templates_path or (mazure_root / "mazure" / "sync" / "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_path)))

    async def generate_service(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        spec_path: Path
    ) -> Path:
        """
        Generate a service implementation from OpenAPI spec
        """

        # Step 1: Parse OpenAPI spec using AutoRest
        code_model = await self._parse_spec_with_autorest(spec_path)

        # Step 2: Generate Python service code
        service_code = await self._generate_service_code(
            provider, resource_type, api_version, code_model
        )

        # Step 3: Generate Pydantic schemas
        schemas_code = await self._generate_schemas(
            provider, resource_type, api_version, code_model
        )

        # Step 4: Generate API route handlers
        routes_code = await self._generate_routes(
            provider, resource_type, api_version, code_model
        )

        # Step 5: Write files
        output_dir = await self._get_service_output_dir(provider)

        service_file = output_dir / f"{resource_type.lower()}.py"
        with open(service_file, 'w') as f:
            f.write(service_code)

        # Adjusted path
        schemas_dir = self.mazure_root / "mazure" / "schemas"
        schemas_dir.mkdir(exist_ok=True, parents=True)
        schemas_file = schemas_dir / f"{provider.lower().replace('.', '_')}.py"

        # Append or create schemas file
        mode = 'a' if schemas_file.exists() else 'w'
        with open(schemas_file, mode) as f:
            f.write(schemas_code)

        # Generate routes
        # Adjusted path
        routes_dir = self.mazure_root / "mazure" / "api"
        routes_dir.mkdir(exist_ok=True, parents=True)
        routes_file = routes_dir / f"{provider.lower().replace('.', '_')}.py"
        with open(routes_file, 'w') as f:
            f.write(routes_code)

        print(f"Generated service implementation: {service_file}")
        return service_file

    async def _parse_spec_with_autorest(self, spec_path: Path) -> Dict[str, Any]:
        """
        Use AutoRest to parse OpenAPI spec into code model
        """

        import tempfile

        # Use TemporaryDirectory for cleanup
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)

            # Run AutoRest with code model output
            cmd = [
                "autorest",
                "--input-file=" + str(spec_path),
                "--output-folder=" + str(temp_dir),
                "--python",
                "--code-model-v4=true",
                "--output-artifact=code-model-v4"
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode != 0:
                    print(f"AutoRest warning/error: {result.stderr}")

                # Load generated code model
                code_model_file = temp_dir / "code-model-v4.json"
                if code_model_file.exists():
                    with open(code_model_file) as f:
                        return json.load(f)
                else:
                    # Fallback: parse OpenAPI directly
                    return await self._parse_openapi_directly(spec_path)

            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("AutoRest failed or not found, using direct parsing")
                return await self._parse_openapi_directly(spec_path)

    async def _parse_openapi_directly(self, spec_path: Path) -> Dict[str, Any]:
        """Fallback: Parse OpenAPI spec directly without AutoRest"""

        with open(spec_path) as f:
            spec = json.load(f)

        # Convert OpenAPI to simplified code model
        code_model = {
            'operations': [],
            'schemas': spec.get('definitions', {}),
            'paths': spec.get('paths', {}),
            'info': spec.get('info', {})
        }

        # Parse operations from paths
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                if method.upper() in ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']:
                    code_model['operations'].append({
                        'path': path,
                        'method': method.upper(),
                        'operation_id': operation.get('operationId'),
                        'parameters': operation.get('parameters', []),
                        'responses': operation.get('responses', {}),
                        'summary': operation.get('summary'),
                        'description': operation.get('description')
                    })

        return code_model

    async def _generate_service_code(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        code_model: Dict[str, Any]
    ) -> str:
        """Generate service implementation Python code"""

        template = self.jinja_env.get_template('service.py.jinja2')

        # Extract operations
        operations = code_model.get('operations', [])

        # Categorize operations
        crud_operations = {
            'create': None,
            'get': None,
            'list': None,
            'update': None,
            'delete': None
        }

        for op in operations:
            op_id = op.get('operation_id', '').lower()

            if 'create' in op_id or (op['method'] == 'PUT' and '{' in op['path']):
                crud_operations['create'] = op
            elif ('get' in op_id or 'list' in op_id) and op['method'] == 'GET':
                # Heuristic: if path ends with parameter, it's likely a get item
                # if path ends with segment, it's likely a list
                # But here we use existence of '{' which works if list is on collection
                # However, sub-resources also have '{' in path.
                # E.g. /subs/{id}/rg/{name}/providers/Microsoft.Dummy/dummies
                # vs /subs/{id}/rg/{name}/providers/Microsoft.Dummy/dummies/{dummyName}

                # We can check if the last segment is a parameter
                is_item = op['path'].strip('/').split('/')[-1].startswith('{')

                if is_item:
                    crud_operations['get'] = op
                else:
                    crud_operations['list'] = op
            elif 'update' in op_id or op['method'] == 'PATCH':
                crud_operations['update'] = op
            elif 'delete' in op_id or op['method'] == 'DELETE':
                crud_operations['delete'] = op

        return template.render(
            provider=provider,
            resource_type=resource_type,
            api_version=api_version,
            operations=crud_operations,
            all_operations=operations,
            timestamp=datetime.utcnow().isoformat()
        )

    async def _generate_schemas(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        code_model: Dict[str, Any]
    ) -> str:
        """Generate Pydantic schema models"""

        template = self.jinja_env.get_template('schemas.py.jinja2')

        schemas = code_model.get('schemas', {})

        return template.render(
            provider=provider,
            resource_type=resource_type,
            schemas=schemas,
            timestamp=datetime.utcnow().isoformat()
        )

    async def _generate_routes(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        code_model: Dict[str, Any]
    ) -> str:
        """Generate FastAPI/Flask route handlers"""

        template = self.jinja_env.get_template('routes.py.jinja2')

        operations = code_model.get('operations', [])
        service_package = self._get_service_package_name(provider)

        return template.render(
            provider=provider,
            resource_type=resource_type,
            api_version=api_version,
            operations=operations,
            service_package=service_package,
            timestamp=datetime.utcnow().isoformat()
        )

    def _get_service_package_name(self, provider: str) -> str:
        """Get the package name for the provider"""
        provider_mapping = {
            'Microsoft.Compute': 'compute',
            'Microsoft.Network': 'network',
            'Microsoft.Storage': 'storage',
            'Microsoft.Resources': 'resources',
            'Microsoft.Authorization': 'authorization',
            'Microsoft.KeyVault': 'keyvault',
            'Microsoft.Web': 'web',
            'Microsoft.Sql': 'sql',
        }
        return provider_mapping.get(provider, provider.lower().replace('microsoft.', ''))

    async def _get_service_output_dir(self, provider: str) -> Path:
        """Get output directory for service code"""

        dir_name = self._get_service_package_name(provider)
        # Adjusted path
        output_dir = self.mazure_root / "mazure" / "services" / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir
