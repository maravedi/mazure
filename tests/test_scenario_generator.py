import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from mazure.scenarios.generator import ScenarioGenerator

@pytest.fixture
def temp_scenario_file(tmp_path):
    scenario = [
        {
            "provider": "Microsoft.Compute",
            "resource_type": "virtualMachines",
            "name": "test-vm",
            "properties": {"foo": "bar"}
        }
    ]
    p = tmp_path / "test_scenario.json"
    with open(p, "w") as f:
        json.dump(scenario, f)
    return p

def test_load_template(temp_scenario_file):
    # Pass the parent of the temp file as mazure_root,
    # but the generator looks for mazure/scenarios/templates relative to root.
    # So we better pass the full path to the file as template_name

    # Actually, ScenarioGenerator has a fallback:
    # 1. checks if exists as path
    # 2. checks in templates dir

    gen = ScenarioGenerator(str(temp_scenario_file), Path("/tmp"))
    assert len(gen.data) == 1
    assert gen.data[0]["name"] == "test-vm"

def test_generate_script(temp_scenario_file, tmp_path):
    gen = ScenarioGenerator(str(temp_scenario_file), Path("/tmp"))
    out_path = tmp_path / "output_script.py"
    gen.generate_script(out_path)

    assert out_path.exists()
    content = out_path.read_text()
    assert "requests.put" in content
    assert "test-vm" in content
    assert "Microsoft.Compute" in content
    assert 'url = f"{host}/subscriptions/{subscription_id}/resourceGroups/{name}"' in content or 'url = f"{host}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{provider}/{resource_type}/{name}"' in content

@patch("requests.put")
def test_apply(mock_put, temp_scenario_file):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_put.return_value = mock_response

    gen = ScenarioGenerator(str(temp_scenario_file), Path("/tmp"))
    gen.apply("http://test-host:1234")

    mock_put.assert_called_once()
    args, kwargs = mock_put.call_args
    url = args[0]
    assert "http://test-host:1234" in url
    assert "/providers/Microsoft.Compute/virtualMachines/test-vm" in url
    assert kwargs['json'] == {"foo": "bar"}

@patch("requests.put")
def test_apply_resource_group(mock_put, tmp_path):
    scenario = [
        {
            "provider": "Microsoft.Resources",
            "resource_type": "resourceGroups",
            "name": "test-rg",
            "subscription_id": "sub123",
            "properties": {}
        }
    ]
    p = tmp_path / "rg_scenario.json"
    with open(p, "w") as f:
        json.dump(scenario, f)

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_put.return_value = mock_response

    gen = ScenarioGenerator(str(p), Path("/tmp"))
    gen.apply("http://test-host:1234")

    mock_put.assert_called_once()
    args, kwargs = mock_put.call_args
    url = args[0]
    assert "http://test-host:1234/subscriptions/sub123/resourceGroups/test-rg" == url
