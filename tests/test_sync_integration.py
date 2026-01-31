import pytest
import os
from pathlib import Path
import json
import shutil
import asyncio
from mazure.sync.codegen import MazureCodeGenerator
from mazure.services import app
from mazure.services.utils import discover_generated_services

@pytest.mark.asyncio
async def test_codegen_and_registration():
    # 1. Setup Spec
    spec_content = {
        "swagger": "2.0",
        "info": {"title": "TestService", "version": "2024-01-01"},
        "paths": {
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Test/testResources/{resourceName}": {
                "put": {
                    "operationId": "TestResources_CreateOrUpdate",
                    "description": "Create test resource",
                    "responses": {"200": {"description": "OK"}},
                    "parameters": [
                        {"name": "subscriptionId", "in": "path", "required": True, "type": "string"},
                        {"name": "resourceGroupName", "in": "path", "required": True, "type": "string"},
                        {"name": "resourceName", "in": "path", "required": True, "type": "string"}
                    ]
                }
            }
        }
    }

    spec_path = Path("test_spec.json")
    with open(spec_path, "w") as f:
        json.dump(spec_content, f)

    mazure_root = Path.cwd()

    # 2. Run CodeGen
    generator = MazureCodeGenerator(
        specs_path=spec_path,
        mazure_root=mazure_root
    )

    # Track files to clean up
    files_to_clean = []
    dirs_to_clean = []

    try:
        print("Generating service...")
        service_file = await generator.generate_service(
            provider="Microsoft.Test",
            resource_type="testResources",
            api_version="2024-01-01",
            spec_path=spec_path
        )

        # Verify files created
        api_file = mazure_root / "mazure/api/microsoft_test_testresources.py"
        files_to_clean.append(api_file)
        assert api_file.exists(), f"{api_file} not created"

        init_file = mazure_root / "mazure/api/__init__.py"
        # We don't delete init file as it might be needed by others/project, but for this test it's fine if we leave it or check if it was there before.
        # Assuming it wasn't there or is fine to stay.
        assert init_file.exists()

        service_file_path = mazure_root / "mazure/services/test/testresources.py"
        files_to_clean.append(service_file_path)
        dirs_to_clean.append(mazure_root / "mazure/services/test")

        schema_file = mazure_root / "mazure/schemas/microsoft_test.py"
        files_to_clean.append(schema_file)

        # 3. Discover services
        print("Discovering generated services...")
        generated = discover_generated_services(app)

        # Find our service
        found = False
        test_bp = None
        for category, services in generated.items():
            print(f"Category: {category}")
            for svc in services:
                print(f"  Blueprint: {svc.blueprint.name}")
                if "testresources" in svc.blueprint.name:
                    found = True
                    test_bp = svc.blueprint

        assert found, "Generated service not discovered"

        # Register manually for verification (since app was imported before generation)
        if test_bp.name not in app.blueprints:
            app.register_blueprint(test_bp)

        # 4. Verify Route
        print("Verifying routes...")
        found_rule = False
        target_path = "/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Test/testResources/<resourceName>"

        for rule in app.url_map.iter_rules():
             # rule.rule is the path
             if "Microsoft.Test" in rule.rule and "testResources" in rule.rule:
                 found_rule = True
                 print(f"Found rule: {rule.rule}")
                 break

        assert found_rule, "Route not found in app.url_map"

    finally:
        # Cleanup
        if spec_path.exists():
            spec_path.unlink()

        for f in files_to_clean:
            if f.exists():
                f.unlink()

        for d in dirs_to_clean:
            if d.exists() and not any(d.iterdir()):
                d.rmdir()
