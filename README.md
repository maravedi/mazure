# Mazure - Azure Mock Service

Mazure is a mocking framework for Azure services, similar to [Moto](https://github.com/spulec/moto) for AWS. It allows you to test Azure-dependent code without making actual API calls to Azure.

## Features

### Core Capabilities
- **Service Mocking**: Mock Azure Resource Manager APIs for testing
- **State Management**: MongoDB-backed resource state for realistic behavior
- **Code Generation**: AutoRest-based service implementation generator
- **API Coverage**: Growing support for Compute, Storage, Network, and more

### Discovery Integration (✅ COMPLETE)
- **Seed from Live Azure**: Import real Azure topology into mock state
- **Snapshot Fixtures**: Create deterministic test environments from production
- **Relationship Tracking**: Model resource dependencies for cascading operations
- **Query Engines**: KQL (Resource Graph) and OData (Microsoft Graph) support
- **Schema Generation**: Auto-generate Pydantic models from discovered resources
- **Mock Validation**: Compare mock implementations against live Azure
- **Multi-Cloud Support**: Works with Azure Government, China, and other clouds

**✨ NEW:** See [Discovery Integration README](README_DISCOVERY_INTEGRATION.md) for complete features and quick start guide.

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

### Discovery Integration Quick Start

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

### Query with Resource Graph or Microsoft Graph

```bash
# Start the server
python -m uvicorn mazure.app:app --reload --port 8000

# Query Resource Graph (KQL)
curl -X POST http://localhost:8000/providers/Microsoft.ResourceGraph/resources \
  -H "Content-Type: application/json" \
  -d '{"subscriptions":["sub-id"],"query":"Resources | where type =~ '"'"'Microsoft.Compute/virtualMachines'"'"' | take 10"}'

# Query Microsoft Graph (OData)
curl "http://localhost:8000/v1.0/users?\$top=5&\$filter=startswith(displayName,'John')"
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
  -e, --environment TEXT      Azure environment

# Manage snapshots
mazure snapshot list [--dir PATH]    # List available snapshots
mazure snapshot load PATH [--clear]  # Load snapshot into state

# Validation commands (NEW!)
mazure validate service SNAPSHOT_FILE [-t TYPE] [-o OUTPUT]  # Validate mock against discovery
mazure validate schema SNAPSHOT_FILE TYPE [-e FILE]          # Generate/validate schema

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

### Discovery Integration (All Phases Complete)

#### ✅ Phase 1: Foundation
- Import Azure resources via AzureDiscovery
- Store relationships for dependency tracking
- Export/import snapshots as test fixtures
- CLI commands for seeding and snapshot management

#### ✅ Phase 2: Query Engines
- **Resource Graph Service**: Full KQL query support (WHERE, PROJECT, SUMMARIZE, etc.)
- **Microsoft Graph API**: Users, groups, OData parameters
- FastAPI routes with pagination
- MongoDB-backed state queries

#### ✅ Phase 3: Intelligence Layer
- **ResponseSynthesizer**: Generate realistic resources from patterns
- **SchemaGenerator**: Auto-generate Pydantic models from discovery data
- **DiscoveryBasedValidator**: Compare mocks against live Azure
- CLI validation commands

#### ✅ Phase 4: Production Hardening
- Error scenario simulation (429, 404, 500, etc.)
- Performance benchmarks and optimization
- MongoDB indexes for fast queries
- Integration test suite
- Comprehensive documentation

See [Complete Checklist](COMPLETE_CHECKLIST.md) for detailed implementation status.

## Documentation

### Getting Started
- **[Discovery Integration README](README_DISCOVERY_INTEGRATION.md)** - Quick start and complete guide
- **[Complete Checklist](COMPLETE_CHECKLIST.md)** - All features and how to use them
- **[Phase 2 Features](PHASE2_FEATURES.md)** - Query engine documentation

### Architecture & Planning
- **[Integration Plan](AzureDiscoveryIntegrationPlan.md)** - Full implementation roadmap
- **[Implementation Status](IMPLEMENTATION_STATUS.md)** - Phase tracking
- **[Improvement Plan](ImprovementPlan.md)** - Overall mazure roadmap

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

# Setup database indexes
python scripts/setup_mongodb_indexes.py
```

### Running Tests
```bash
# All tests with one command
sh scripts/run_all_tests.sh

# Or individually:
pytest tests/unit                      # Unit tests
pytest tests/integration               # Integration tests (requires MongoDB)
pytest --cov=mazure tests/             # With coverage

# Run benchmarks
python scripts/benchmark_queries.py

# Run examples
python examples/query_examples.py
```

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

**Phase 1 (Discovery Integration - Foundation)**: ✅ Complete
- State seeding from Azure
- Snapshot management
- CLI commands
- Relationship tracking

**Phase 2 (Query Engines)**: ✅ Complete
- Resource Graph KQL queries
- Microsoft Graph API mocks
- FastAPI routes
- Pagination support

**Phase 3 (Intelligence Layer)**: ✅ Complete
- Response synthesis
- Schema generation
- Discovery-based validation
- CLI validation commands

**Phase 4 (Production Hardening)**: ✅ Complete
- Error scenario simulation
- Performance optimization
- Integration tests
- Comprehensive documentation

---

**All discovery integration phases are complete!** ✅

See [README_DISCOVERY_INTEGRATION.md](README_DISCOVERY_INTEGRATION.md) for the complete guide.
