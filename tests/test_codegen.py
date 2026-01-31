import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json
import tempfile
import shutil
from mazure.sync.codegen import MazureCodeGenerator

class TestMazureCodeGenerator(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mazure_root = Path(self.temp_dir)
        self.specs_path = Path(self.temp_dir) / "specs"
        self.specs_path.mkdir()

        self.real_mazure_root = Path.cwd()
        self.templates_path = self.real_mazure_root / "mazure" / "sync" / "templates"

    async def asyncTearDown(self):
        shutil.rmtree(self.temp_dir)

    async def test_generate_service(self):
        # Create a dummy spec file
        spec_content = {
            "swagger": "2.0",
            "info": {"title": "Test", "version": "2021-01-01"},
            "paths": {
                "/subscriptions/{s}/resourceGroups/{r}/providers/Microsoft.Test/tests/{n}": {
                    "put": {
                        "operationId": "Tests_CreateOrUpdate",
                        "description": "Create test",
                        "responses": {"200": {"description": "OK"}}
                    },
                    "get": {
                        "operationId": "Tests_Get",
                        "description": "Get test",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            },
            "definitions": {
                "TestResource": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }

        spec_file = self.specs_path / "test.json"
        with open(spec_file, "w") as f:
            json.dump(spec_content, f)

        generator = MazureCodeGenerator(
            specs_path=self.specs_path,
            mazure_root=self.mazure_root,
            templates_path=self.templates_path
        )

        with patch('subprocess.run', side_effect=FileNotFoundError):
            output_file = await generator.generate_service(
                provider="Microsoft.Test",
                resource_type="tests",
                api_version="2021-01-01",
                spec_path=spec_file
            )

        # Verify output
        self.assertTrue(output_file.exists())
        content = output_file.read_text()
        self.assertIn("class TestsService", content)
        self.assertIn("def create_or_update", content)
        self.assertIn("def get", content)

        # Verify schema file created
        schema_file = self.mazure_root / "mazure" / "schemas" / "microsoft_test.py"
        self.assertTrue(schema_file.exists())

        # Verify routes file created
        routes_file = self.mazure_root / "mazure" / "api" / "microsoft_test.py"
        self.assertTrue(routes_file.exists())
