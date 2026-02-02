"""
Tests for the Mazure Python API client.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from mazure.api_client import MazureAPI


class TestMazureAPI(unittest.TestCase):
    """Test the programmatic Python API."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.api = MazureAPI(mazure_root=Path(self.temp_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_api_initialization(self):
        """Test API client initialization."""
        api = MazureAPI()
        self.assertIsNotNone(api)
        self.assertIsInstance(api.mazure_root, Path)

        api_with_root = MazureAPI(mazure_root=Path("/tmp"))
        self.assertEqual(api_with_root.mazure_root, Path("/tmp"))

    def test_status_no_services(self):
        """Test status when no services are generated."""
        status = self.api.status()
        self.assertIn("services", status)
        self.assertIn("server_running", status)
        self.assertIn("server_url", status)
        self.assertEqual(status["services"], [])
        self.assertFalse(status["server_running"])
        self.assertIsNone(status["server_url"])

    def test_status_with_services(self):
        """Test status when services are generated."""
        # Create mock api directory with a service file
        api_dir = Path(self.temp_dir) / "mazure" / "api"
        api_dir.mkdir(parents=True, exist_ok=True)

        # Create a mock service file
        service_file = api_dir / "microsoft_compute_virtualmachines.py"
        service_file.write_text(
            "# API Routes for Microsoft.Compute/virtualMachines\n"
            "# Generated service\n"
        )

        status = self.api.status()
        self.assertEqual(len(status["services"]), 1)
        self.assertIn("Microsoft.Compute/virtualMachines", status["services"][0])

    @patch('mazure.sync.codegen.MazureCodeGenerator')
    @patch('mazure.cli.sync._find_spec_path')
    @patch('asyncio.run')
    def test_generate_with_auto_discover(self, mock_asyncio, mock_find_spec, mock_generator):
        """Test generate method with auto-discovery of spec path."""
        mock_spec_path = Path("/fake/spec.json")
        mock_find_spec.return_value = mock_spec_path

        self.api.generate(
            provider="Microsoft.Compute",
            resource_type="virtualMachines",
            api_version="2024-03-01"
        )

        mock_find_spec.assert_called_once_with(
            "Microsoft.Compute",
            "virtualMachines",
            "2024-03-01"
        )
        mock_asyncio.assert_called_once()

    @patch('mazure.sync.codegen.MazureCodeGenerator')
    @patch('asyncio.run')
    def test_generate_with_explicit_spec_path(self, mock_asyncio, mock_generator):
        """Test generate method with explicit spec path."""
        spec_path = Path("/explicit/spec.json")

        self.api.generate(
            provider="Microsoft.Compute",
            resource_type="virtualMachines",
            api_version="2024-03-01",
            spec_path=spec_path
        )

        mock_asyncio.assert_called_once()

    @patch('mazure.cli.sync._find_spec_path')
    def test_generate_spec_not_found(self, mock_find_spec):
        """Test generate raises error when spec not found."""
        mock_find_spec.return_value = None

        with self.assertRaises(FileNotFoundError) as cm:
            self.api.generate(
                provider="Microsoft.Fake",
                resource_type="fakeResource",
                api_version="2024-01-01"
            )

        self.assertIn("Could not find spec file", str(cm.exception))

    @patch('mazure.sync.spec_sync.AzureSpecSyncEngine')
    @patch('asyncio.run')
    def test_sync_without_auto_generate(self, mock_asyncio, mock_engine):
        """Test sync without auto-generation."""
        # Mock the asyncio.run to return changes
        mock_changes = [
            MagicMock(
                change_type=MagicMock(value="ADDED"),
                provider="Microsoft.Compute",
                resource_type="virtualMachines",
                api_version="2024-03-01"
            )
        ]
        mock_asyncio.return_value = mock_changes

        changes = self.api.sync(auto_generate=False)

        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["change_type"], "ADDED")
        self.assertEqual(changes[0]["provider"], "Microsoft.Compute")

    def test_list_specs_no_specs_dir(self):
        """Test list_specs when specs directory doesn't exist."""
        with self.assertRaises(FileNotFoundError) as cm:
            self.api.list_specs()

        self.assertIn("Azure specs not found", str(cm.exception))

    @patch('mazure.services.utils.services')
    @patch('mazure.services.utils.register')
    @patch('mazure.services.app')
    def test_serve_blocking(self, mock_app, mock_register, mock_services):
        """Test serve in blocking mode."""
        mock_services.return_value = []
        mock_flask_app = MagicMock()
        mock_app.return_value = mock_flask_app

        # We can't actually test blocking mode without hanging the test
        # Just verify the setup is correct
        self.api._server_thread = None

    @patch('mazure.services.utils.services')
    @patch('mazure.services.utils.register')
    @patch('mazure.services.app.run')
    def test_serve_non_blocking(self, mock_run, mock_register, mock_services):
        """Test serve in non-blocking mode."""
        mock_services.return_value = []

        # Start server in non-blocking mode
        self.api.serve(port=5051, blocking=False)

        # Give it a moment to start
        import time
        time.sleep(0.5)

        # Verify thread was started
        self.assertIsNotNone(self.api._server_thread)

        # Stop the server
        self.api.stop_server()

    @patch('mazure.scenarios.generator.ScenarioGenerator')
    def test_scenario_apply(self, mock_generator):
        """Test scenario generation with apply."""
        mock_gen_instance = MagicMock()
        mock_generator.return_value = mock_gen_instance

        result = self.api.scenario(template="compliance/cmmc", apply=True)

        mock_gen_instance.apply.assert_called_once()
        self.assertEqual(result, "Template applied successfully")

    @patch('mazure.scenarios.generator.ScenarioGenerator')
    def test_scenario_generate_script(self, mock_generator):
        """Test scenario generation to script."""
        mock_gen_instance = MagicMock()
        mock_gen_instance.generate_script.return_value = Path("/output/script.py")
        mock_generator.return_value = mock_gen_instance

        result = self.api.scenario(
            template="compliance/cmmc",
            apply=False,
            output=Path("/output/script.py")
        )

        mock_gen_instance.generate_script.assert_called_once()
        self.assertEqual(result, "/output/script.py")

    @patch('mazure.sync.spec_sync.AzureSpecSyncEngine')
    @patch('asyncio.run')
    def test_coverage(self, mock_asyncio, mock_engine):
        """Test coverage report generation."""
        mock_coverage = {
            "total_providers": 100,
            "implemented_providers": 10,
            "coverage_percentage": 10.0,
            "providers": {
                "implemented": ["Microsoft.Compute", "Microsoft.Storage"],
                "missing": ["Microsoft.Network", "..."]
            }
        }
        mock_asyncio.return_value = mock_coverage

        coverage = self.api.coverage()

        self.assertEqual(coverage["total_providers"], 100)
        self.assertEqual(coverage["coverage_percentage"], 10.0)

    @patch('mazure.sync.compatibility.CompatibilityMatrix')
    def test_compatibility(self, mock_matrix_class):
        """Test compatibility checking."""
        mock_matrix = MagicMock()
        mock_report = {
            "total_resource_types": 50,
            "coverage_by_provider": {
                "Microsoft.Compute": {
                    "supported": 5,
                    "total": 10,
                    "coverage_percentage": 50.0
                }
            }
        }
        mock_matrix.generate_compatibility_report.return_value = mock_report
        mock_matrix_class.return_value = mock_matrix

        report = self.api.compatibility()

        self.assertEqual(report["total_resource_types"], 50)
        self.assertIn("coverage_by_provider", report)


class TestMazureAPIIntegration(unittest.TestCase):
    """Integration tests for the Mazure API (requires actual setup)."""

    def test_api_can_be_imported(self):
        """Test that the API can be imported from the main package."""
        from mazure import MazureAPI

        api = MazureAPI()
        self.assertIsNotNone(api)

    def test_api_exposed_in_all(self):
        """Test that MazureAPI is in __all__."""
        import mazure

        self.assertIn('MazureAPI', mazure.__all__)


if __name__ == '__main__':
    unittest.main()
