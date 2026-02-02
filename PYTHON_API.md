# Mazure Python API Documentation

Mazure provides both a CLI tool and a comprehensive Python API for programmatic access to all functionality. This allows you to integrate Mazure into your Python applications, test frameworks, or automation scripts.

## Installation

```bash
pip install mazure
```

## Quick Start

```python
from mazure import MazureAPI

# Initialize the API client
api = MazureAPI()

# Check status of generated services
status = api.status()
print(f"Generated services: {status['services']}")
print(f"Server running: {status['server_running']}")

# Start the mock server (non-blocking)
api.serve(port=5050, blocking=False)

# Generate a new service
api.generate(
    provider="Microsoft.Compute",
    resource_type="virtualMachines",
    api_version="2024-03-01"
)

# Stop the server when done
api.stop_server()
```

## API Reference

### MazureAPI Class

The main API client for interacting with Mazure programmatically.

#### Initialization

```python
from mazure import MazureAPI

api = MazureAPI(mazure_root="/path/to/project")  # Optional: defaults to current directory
```

### Methods

#### `generate(provider, resource_type, api_version, spec_path=None)`

Generate service implementation from OpenAPI specification.

**Parameters:**
- `provider` (str): Provider namespace (e.g., "Microsoft.Compute")
- `resource_type` (str): Resource type (e.g., "virtualMachines")
- `api_version` (str): API version (e.g., "2024-03-01")
- `spec_path` (Path, optional): Path to spec file (auto-discovered if not provided)

**Returns:** None

**Raises:**
- `FileNotFoundError`: If spec file not found
- `RuntimeError`: If generation fails

**Example:**
```python
# Auto-discover spec file
api.generate(
    provider="Microsoft.Storage",
    resource_type="storageAccounts",
    api_version="2023-01-01"
)

# Explicit spec path
from pathlib import Path
api.generate(
    provider="Microsoft.Compute",
    resource_type="virtualMachines",
    api_version="2024-03-01",
    spec_path=Path("specs/azure-rest-api-specs/specification/compute/resource-manager/Microsoft.Compute/ComputeRP/stable/2024-03-01/virtualMachines.json")
)
```

#### `serve(port=5050, host="0.0.0.0", blocking=True, debug=False)`

Start the Mazure mock server.

**Parameters:**
- `port` (int): Port to run the server on (default: 5050)
- `host` (str): Host to bind to (default: "0.0.0.0")
- `blocking` (bool): If True, blocks until server stops. If False, runs in background thread (default: True)
- `debug` (bool): Enable Flask debug mode (default: False)

**Returns:** None

**Example:**
```python
# Blocking mode (for standalone scripts)
api.serve(port=5050)

# Non-blocking mode (for tests or integration)
api.serve(port=5050, blocking=False)
# ... do other work ...
api.stop_server()
```

#### `stop_server()`

Stop the background server if running in non-blocking mode.

**Returns:** None

#### `sync(specs_path=Path("specs/azure-rest-api-specs"), auto_generate=False)`

Sync with latest Azure API specifications.

**Parameters:**
- `specs_path` (Path): Path to azure-rest-api-specs repository
- `auto_generate` (bool): Automatically generate code for changes (default: False)

**Returns:** List[Dict[str, Any]] - List of changes detected

**Example:**
```python
changes = api.sync(
    specs_path=Path("specs/azure-rest-api-specs"),
    auto_generate=True
)

for change in changes:
    print(f"{change['change_type']}: {change['provider']}/{change['resource_type']} v{change['api_version']}")
```

#### `status()`

Get status of generated services and server.

**Returns:** Dict with keys:
- `services` (List[str]): List of generated service names
- `server_running` (bool): Whether the server is running
- `server_url` (str | None): URL of server if running

**Example:**
```python
status = api.status()
print(f"Services: {', '.join(status['services'])}")
if status['server_running']:
    print(f"Server URL: {status['server_url']}")
else:
    print("Server is not running")
```

#### `list_specs(service=None, provider=None, resource=None, query=None)`

List available services, providers, and resources from synced specs.

**Parameters:**
- `service` (str, optional): Service name (e.g., "compute")
- `provider` (str, optional): Provider namespace (e.g., "Microsoft.Compute")
- `resource` (str, optional): Resource type (e.g., "virtualMachines")
- `query` (str, optional): Search string

**Returns:** Dict with available items

**Example:**
```python
# List all services
services = api.list_specs()
print(services['services'])

# List providers in a service
providers = api.list_specs(service="compute")
print(providers['providers'])

# List resources for a provider
resources = api.list_specs(service="compute", provider="Microsoft.Compute")
print(resources['resources'])

# Get versions for a resource
versions = api.list_specs(
    service="compute",
    provider="Microsoft.Compute",
    resource="virtualMachines"
)
print(versions['versions'])

# Search for resources
results = api.list_specs(query="storage")
print(results['matches'])
```

#### `coverage()`

Get API coverage report.

**Returns:** Dict with coverage statistics

**Example:**
```python
coverage = api.coverage()
print(f"Total providers: {coverage['total_providers']}")
print(f"Implemented: {coverage['implemented_providers']}")
print(f"Coverage: {coverage['coverage_percentage']}%")
```

#### `compatibility(specs_path=Path("specs/azure-rest-api-specs"))`

Check API version compatibility.

**Parameters:**
- `specs_path` (Path): Path to azure-rest-api-specs repository

**Returns:** Dict with compatibility report

**Example:**
```python
report = api.compatibility()
print(f"Total resource types: {report['total_resource_types']}")
for provider, data in report['coverage_by_provider'].items():
    if data['supported'] > 0:
        print(f"{provider}: {data['coverage_percentage']}%")
```

#### `scenario(template, apply=False, output=None)`

Generate environment state from template.

**Parameters:**
- `template` (str): Template name (e.g., "compliance/cmmc")
- `apply` (bool): Apply the template directly to the running server (default: False)
- `output` (Path, optional): Output path for generated script

**Returns:** str - Path to generated script or success message

**Example:**
```python
# Generate script
script_path = api.scenario(
    template="compliance/cmmc",
    output=Path("setup_compliance.py")
)
print(f"Script generated: {script_path}")

# Apply directly
api.scenario(template="compliance/cmmc", apply=True)
```

## Complete Example: Integration Testing

Here's a complete example showing how to use the Mazure Python API in integration tests:

```python
import unittest
from pathlib import Path
from mazure import MazureAPI
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

class TestAzureIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Mazure mock server for all tests."""
        cls.api = MazureAPI()

        # Generate required services
        cls.api.generate(
            provider="Microsoft.Compute",
            resource_type="virtualMachines",
            api_version="2024-03-01"
        )

        cls.api.generate(
            provider="Microsoft.Resources",
            resource_type="resourceGroups",
            api_version="2021-04-01"
        )

        # Start server in non-blocking mode
        cls.api.serve(port=5050, blocking=False)

        # Give server time to start
        import time
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Stop the mock server."""
        cls.api.stop_server()

    def test_create_vm(self):
        """Test creating a virtual machine against Mazure."""
        import os

        # Point Azure SDK to Mazure
        os.environ['AZURE_AUTHORITY_HOST'] = 'http://localhost:5050'

        # Create Azure client (will connect to Mazure)
        credential = DefaultAzureCredential()
        compute_client = ComputeManagementClient(
            credential=credential,
            subscription_id="test-subscription",
            base_url="http://localhost:5050"
        )

        # Make API calls - these will be handled by Mazure
        vm = compute_client.virtual_machines.begin_create_or_update(
            resource_group_name="test-rg",
            vm_name="test-vm",
            parameters={
                "location": "eastus",
                "hardware_profile": {
                    "vm_size": "Standard_DS1_v2"
                },
                "storage_profile": {
                    "image_reference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "18.04-LTS",
                        "version": "latest"
                    }
                }
            }
        ).result()

        self.assertEqual(vm.name, "test-vm")
        self.assertEqual(vm.location, "eastus")

if __name__ == '__main__':
    unittest.main()
```

## Using with Context Manager

You can also use the `Mazure` context manager from the main package for decorator-based mocking:

```python
from mazure import Mazure

# As context manager
with Mazure(['compute'], allow=False):
    # Your Azure SDK calls here will be mocked
    pass

# As decorator
from mazure import mazure

@mazure('compute')
def test_something():
    # Azure compute calls will be mocked
    pass
```

## Advantages of Python API

The Python API provides several advantages over CLI usage:

1. **Integration Testing**: Easily integrate into your test suites
2. **Automation**: Build automated workflows that generate and update services
3. **Custom Tools**: Create custom tooling around Mazure functionality
4. **CI/CD**: Integrate into CI/CD pipelines programmatically
5. **Dynamic Configuration**: Generate services on-demand based on runtime requirements

## Comparison with CLI

| Feature | CLI | Python API |
|---------|-----|------------|
| Generate services | `mazure generate Microsoft.Compute virtualMachines 2024-03-01` | `api.generate("Microsoft.Compute", "virtualMachines", "2024-03-01")` |
| Start server | `mazure serve --port 5050` | `api.serve(port=5050, blocking=False)` |
| Check status | `mazure status` | `status = api.status()` |
| Sync specs | `mazure sync --auto-generate` | `api.sync(auto_generate=True)` |
| List specs | `mazure list compute Microsoft.Compute` | `api.list_specs("compute", "Microsoft.Compute")` |

## Best Practices

1. **Non-blocking Server**: Use `blocking=False` when integrating with tests or applications
2. **Resource Cleanup**: Always call `stop_server()` when using non-blocking mode
3. **Error Handling**: Wrap API calls in try-except blocks to handle errors gracefully
4. **Path Management**: Use `pathlib.Path` for file paths for cross-platform compatibility
5. **Test Isolation**: Create a new `MazureAPI` instance for each test class or suite

## Troubleshooting

### Server Already Running

```python
status = api.status()
if status['server_running']:
    print("Server is already running at", status['server_url'])
else:
    api.serve(port=5050, blocking=False)
```

### Spec Not Found

```python
try:
    api.generate("Microsoft.Unknown", "resource", "2024-01-01")
except FileNotFoundError as e:
    print(f"Error: {e}")
    # Try searching for similar specs
    results = api.list_specs(query="unknown")
    print("Did you mean:", results['matches'])
```

### Import Errors

Make sure Mazure is properly installed:

```bash
pip install -e .  # For development
# or
pip install mazure  # For production
```

## See Also

- [README.md](README.md) - Main documentation
- [CLI Documentation](README.md#cli-commands) - CLI command reference
- [Architecture Guide](ImprovementPlan.md) - System architecture
