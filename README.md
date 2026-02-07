# Mazure - Azure Mock Service

Mazure is a mocking framework for Azure services, similar to [Moto](https://github.com/spulec/moto) for AWS. It allows you to test Azure-dependent code without making actual API calls to Azure.

## Features

### Core Capabilities
- **Service Mocking**: Mock Azure Resource Manager APIs for testing
- **State Management**: MongoDB-backed resource state for realistic behavior
- **Code Generation**: AutoRest-based service implementation generator
- **API Coverage**: Growing support for Compute, Storage, Network, and more

### Discovery Integration (NEW! 🎉)
- **Seed from Live Azure**: Import real Azure topology into mock state
- **Snapshot Fixtures**: Create deterministic test environments from production
- **Relationship Tracking**: Model resource dependencies for cascading operations
- **Multi-Cloud Support**: Works with Azure Government, China, and other clouds

See [Discovery Integration Documentation](docs/DiscoveryIntegration.md) for details.

## Quick Start

### Installation

```bash
pip install mazure

# For discovery integration
pip install mazure[discovery]
```

### Basic Usage

```python
from mazure import mazure
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential

@mazure
def test_create_vm():
    client = ComputeManagementClient(
        DefaultAzureCredential(),
        'subscription-id'
    )
    
    # Create VM - mocked by mazure
    vm = client.virtual_machines.begin_create_or_update(
        'resource-group',
        'vm-name',
        vm_parameters
    ).result()
    
    assert vm.name == 'vm-name'
```

### Discovery Integration

Seed mazure with real Azure topology:

```bash
# Authenticate with Azure
az login

# Seed from your Azure environment
mazure seed from-azure <tenant-id> -s <subscription-id>

# Or export as reusable snapshot
mazure seed from-azure <tenant-id> --output fixtures/prod.json

# Load snapshot in tests
mazure snapshot load fixtures/prod.json
```

Use in tests:

```python
import pytest
from mazure.scenarios.snapshot_manager import SnapshotManager
from mazure.core.state import StateManager

@pytest.fixture
async def production_topology():
    manager = SnapshotManager()
    await manager.seed_from_snapshot(
        Path('fixtures/prod.json'),
        StateManager()
    )

@mazure
@pytest.mark.usefixtures('production_topology')
def test_with_real_topology():
    # Test against production-like environment
    client = ComputeManagementClient(...)
    vms = list(client.virtual_machines.list_all())
    # VMs from your actual Azure environment!
```

## CLI Commands

### Service Management
```bash
# List available Azure services
mazure list

# Generate service implementation
mazure generate Microsoft.Compute virtualMachines 2024-03-01

# Show coverage report
mazure coverage

# Start mock server
mazure serve --port 5050
```

### Discovery Integration
```bash
# Seed from live Azure
mazure seed from-azure <tenant-id> [options]
  -s, --subscription TEXT     Subscription ID(s) to discover
  --include-entra             Include Entra ID objects
  -o, --output PATH           Export snapshot to file
  -e, --environment TEXT      Azure environment (AZURE_PUBLIC, AZURE_GOVERNMENT, etc.)

# Manage snapshots
mazure snapshot list [--dir PATH]    # List available snapshots
mazure snapshot load PATH [--clear]  # Load snapshot into state

# Server and status
mazure status    # Show generated services and server status
mazure serve     # Start mock API server
```

## Architecture

### State Management
Mazure uses MongoDB to store mock resource state, enabling:
- Persistent state across test runs
- Complex queries and relationships
- Realistic CRUD operations

### Code Generation
AutoRest-based generator creates service implementations from Azure OpenAPI specs:
1. Sync with `azure-rest-api-specs` repository
2. Generate Python service code
3. Auto-register API routes

### Discovery Integration
Phase 1 implementation (complete):
- Import Azure resources via AzureDiscovery
- Store relationships for dependency tracking
- Export/import snapshots as test fixtures
- CLI commands for seeding and snapshot management

See [Integration Plan](AzureDiscoveryIntegrationPlan.md) for roadmap.

## Development

### Setup
```bash
# Clone repository
git clone https://github.com/maravedi/mazure.git
cd mazure

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt

# Install in development mode
pip install -e .

# Start MongoDB
mongod --dbpath /path/to/data
```

### Running Tests
```bash
# Unit tests
pytest tests/unit

# Integration tests (requires MongoDB)
pytest tests/integration

# With coverage
pytest --cov=mazure tests/
```

## Documentation

- [Discovery Integration](docs/DiscoveryIntegration.md) - Azure Discovery integration guide
- [Integration Plan](AzureDiscoveryIntegrationPlan.md) - Full implementation roadmap
- [Improvement Plan](ImprovementPlan.md) - Overall mazure roadmap

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## Related Projects

- [AzureDiscovery](https://github.com/maravedi/AzureDiscovery) - Azure tenant discovery tool
- [Moto](https://github.com/spulec/moto) - AWS mocking library (inspiration)
- [LocalStack](https://github.com/localstack/localstack) - AWS local testing

## Status

**Phase 1 (Discovery Integration)**: Complete ✅
- State seeding from Azure
- Snapshot management
- CLI commands
- Documentation

**Phase 2 (Query Engines)**: Planned 📅
- Resource Graph queries
- Microsoft Graph API mocks
- Relationship queries

**Phase 3 (Intelligence)**: Planned 📅
- Response synthesis
- Schema validation
- Test fixture library

**Phase 4 (Production)**: Planned 📅
- Error scenarios
- Performance optimization
- Comprehensive docs
