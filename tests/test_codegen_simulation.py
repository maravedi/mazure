import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json
import tempfile
import shutil
from mazure.sync.codegen import MazureCodeGenerator

class TestMazureCodeGeneratorSimulation(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mazure_root = Path(self.temp_dir)
        self.specs_path = Path(self.temp_dir) / "specs"
        self.specs_path.mkdir()

        self.real_mazure_root = Path.cwd()
        self.templates_path = self.real_mazure_root / "mazure" / "sync" / "templates"

    async def asyncTearDown(self):
        shutil.rmtree(self.temp_dir)

    async def test_generate_service_with_simulation(self):
        # Create a dummy spec file with simulation needs
        spec_content = {
            "swagger": "2.0",
            "info": {"title": "Test", "version": "2021-01-01"},
            "paths": {
                "/subscriptions/{s}/resourceGroups/{r}/providers/Microsoft.Test/simulated/{n}": {
                    "put": {
                        "operationId": "Simulated_CreateOrUpdate",
                        "description": "Create simulated resource",
                        "parameters": [
                            {
                                "name": "parameters",
                                "in": "body",
                                "required": True,
                                "schema": {
                                    "$ref": "#/definitions/SimulatedResource"
                                }
                            }
                        ],
                        "responses": {"200": {"description": "OK"}}
                    },
                    "get": {
                        "operationId": "Simulated_Get",
                        "description": "Get simulated resource",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            },
            "definitions": {
                "SimulatedResource": {
                    "type": "object",
                    "properties": {
                        "properties": {
                            "$ref": "#/definitions/SimulatedResourceProperties"
                        }
                    }
                },
                "SimulatedResourceProperties": {
                    "type": "object",
                    "properties": {
                        "provisioningState": {
                            "type": "string",
                            "readOnly": True
                        },
                        "defaultConfig": {
                            "type": "string",
                            "default": "standard"
                        },
                        "someId": {
                            "type": "string",
                            "readOnly": True
                        },
                        "userConfig": {
                            "type": "string"
                        }
                    }
                }
            }
        }

        spec_file = self.specs_path / "test_sim.json"
        with open(spec_file, "w") as f:
            json.dump(spec_content, f)

        generator = MazureCodeGenerator(
            specs_path=self.specs_path,
            mazure_root=self.mazure_root,
            templates_path=self.templates_path
        )

        # Force direct parsing by patching subprocess.run to fail
        with patch('subprocess.run', side_effect=FileNotFoundError):
            output_file = await generator.generate_service(
                provider="Microsoft.Test",
                resource_type="simulated",
                api_version="2021-01-01",
                spec_path=spec_file
            )

        # Verify output
        self.assertTrue(output_file.exists())
        content = output_file.read_text()

        # Check for simulation logic
        # 1. provisioningState should be defaulted to 'Succeeded' because it's readOnly
        self.assertIn("'provisioningState' not in", content)
        self.assertIn('[\'provisioningState\'] = "Succeeded"', content)

        # 2. defaultConfig should be set to 'standard' if missing
        self.assertIn("'defaultConfig' not in", content)
        self.assertIn('[\'defaultConfig\'] = "standard"', content)
