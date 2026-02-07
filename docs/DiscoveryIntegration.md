# Azure Discovery Integration

This document describes how to use mazure's Azure Discovery integration features to seed mock state from real Azure environments.

## Overview

Mazure can now import real Azure resource topology using the [AzureDiscovery](https://github.com/maravedi/AzureDiscovery) tool. This enables:

- **Realistic test data**: Mock responses reflect actual Azure resource structures
- **Topology-aware testing**: Test cascading operations and dependencies
- **Deterministic tests**: Snapshot fixtures provide reproducible environments
- **Zero maintenance**: Stays synchronized with Azure API changes automatically

## Installation

Install the required dependencies:

```bash
pip install azure-discovery azure-identity
```

## Quick Start

### 1. Seed from Live Azure

Authenticate with Azure (using Azure CLI, service principal, or managed identity):

```bash
# Using Azure CLI
az login

# Or set service principal environment variables
export AZURE_CLIENT_ID="..."
export AZURE_CLIENT_SECRET="..."
export AZURE_TENANT_ID="..."
```

Seed mazure state from your Azure environment:

```bash
# Seed entire tenant
mazure seed from-azure <tenant-id>

# Seed specific subscriptions
mazure seed from-azure <tenant-id> -s <sub-1> -s <sub-2>

# Include Entra ID objects (users, groups, apps)
mazure seed from-azure <tenant-id> --include-entra

# Export snapshot for later use
mazure seed from-azure <tenant-id> --output fixtures/prod-topology.json
```

### 2. Work with Snapshots

Snapshots are JSON files containing discovered resources and relationships.

```bash
# List available snapshots
mazure snapshot list --dir fixtures

# Load snapshot into mock state
mazure snapshot load fixtures/prod-topology.json

# Clear existing state and load snapshot
mazure snapshot load fixtures/prod-topology.json --clear
```

### 3. Use in Tests

Create pytest fixtures that load snapshots:

```python
# conftest.py
import pytest
import asyncio
from pathlib import Path
from mazure.scenarios.snapshot_manager import SnapshotManager
from mazure.core.state import StateManager

@pytest.fixture(scope='session')
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def azure_production_topology():
    """Load production-like Azure topology"""
    snapshot_path = Path('fixtures/prod-topology.json')
    
    manager = SnapshotManager()
    state = StateManager()
    
    # Load snapshot
    await manager.seed_from_snapshot(snapshot_path, state, clear_existing=True)
    
    yield state
    
    # Cleanup
    from mazure.core.state import GenericResource
    from mazure.core.relationships import ResourceRelationship
    GenericResource.objects.delete()
    ResourceRelationship.objects.delete()
```

Use in tests:

```python
# test_compute.py
import pytest
from mazure import mazure
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential

@mazure
@pytest.mark.usefixtures('azure_production_topology')
def test_list_vms_realistic_topology():
    """Test VM listing with production-like topology"""
    
    # Client connects to mazure mock server
    client = ComputeManagementClient(
        DefaultAzureCredential(),
        'mock-subscription-id'
    )
    
    # List VMs - returns resources from snapshot
    vms = list(client.virtual_machines.list_all())
    
    # Assertions based on known snapshot content
    assert len(vms) > 0
    assert all(vm.location in ['eastus', 'westus2'] for vm in vms)
```

## Advanced Usage

### Programmatic Seeding

Seed state from Python code:

```python
import asyncio
from azure_discovery import AzureDiscoveryRequest, AzureEnvironment
from azure.identity.aio import DefaultAzureCredential
from mazure.seeding.discovery_importer import DiscoveryStateSeeder
from mazure.core.state import StateManager

async def seed_from_azure():
    # Create discovery request
    request = AzureDiscoveryRequest(
        tenant_id='your-tenant-id',
        environment=AzureEnvironment.AZURE_PUBLIC,
        subscriptions=['sub-1', 'sub-2'],
        include_entra=True,
        include_relationships=True
    )
    
    # Get credentials
    credential = DefaultAzureCredential()
    
    # Seed state
    seeder = DiscoveryStateSeeder(StateManager())
    stats = await seeder.seed_from_discovery(request)
    
    print(f"Seeded {stats['arm_resources']} ARM resources")
    print(f"Seeded {stats['entra_objects']} Entra objects")
    print(f"Created {stats['relationships']} relationships")
    
    await credential.close()

asyncio.run(seed_from_azure())
```

### Snapshot Management

```python
import asyncio
from pathlib import Path
from mazure.scenarios.snapshot_manager import SnapshotManager
from mazure.core.state import StateManager

async def manage_snapshots():
    manager = SnapshotManager()
    
    # List snapshots
    snapshots = manager.list_snapshots(Path('fixtures'))
    for snap in snapshots:
        meta = snap['metadata']
        print(f"{snap['path']}: {meta['node_count']} nodes")
    
    # Load specific snapshot
    nodes, rels = await manager.load_snapshot(Path('fixtures/prod.json'))
    
    # Seed into mazure
    await manager.seed_from_snapshot(
        Path('fixtures/prod.json'),
        StateManager(),
        clear_existing=True
    )

asyncio.run(manage_snapshots())
```

### Export Custom Snapshots

```python
import asyncio
from azure_discovery import run_discovery, AzureDiscoveryRequest, AzureEnvironment
from azure.identity.aio import DefaultAzureCredential
from mazure.scenarios.snapshot_manager import SnapshotManager
from pathlib import Path

async def create_custom_snapshot():
    # Discover specific resources
    request = AzureDiscoveryRequest(
        tenant_id='your-tenant-id',
        environment=AzureEnvironment.AZURE_PUBLIC,
        subscriptions=['target-sub'],
        include_entra=False,  # Skip Entra for this snapshot
        include_relationships=True
    )
    
    credential = DefaultAzureCredential()
    response = await run_discovery(request, credential)
    
    # Export as snapshot
    manager = SnapshotManager()
    await manager.export_snapshot(
        response.nodes,
        response.relationships,
        Path('fixtures/custom-scenario.json'),
        metadata={
            'description': 'Custom test scenario',
            'environment': 'test'
        }
    )
    
    await credential.close()

asyncio.run(create_custom_snapshot())
```

## Relationship Tracking

Discovery integration tracks resource relationships, enabling:

### Query Relationships

```python
from mazure.core.relationships import ResourceRelationship

# Find resources that depend on a specific resource
resource_id = "/subscriptions/.../resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1"

# Outbound relationships (resources this depends on)
outbound = ResourceRelationship.find_outbound(
    resource_id,
    relation_types=['depends_on']
)

# Inbound relationships (resources that depend on this)
inbound = ResourceRelationship.find_inbound(
    resource_id,
    relation_types=['depends_on']
)

for rel in inbound:
    print(f"{rel.source_id} depends on {resource_id}")
```

### Cascading Operations

Relationships enable realistic cascading delete behavior:

```python
from mazure.core.relationship_engine import RelationshipEngine
from mazure.core.state import StateManager

async def test_cascade_delete():
    engine = RelationshipEngine(StateManager())
    
    # Delete with cascading to dependent resources
    result = await engine.delete_with_dependents(
        resource_id="/subscriptions/.../virtualMachines/vm1",
        cascade=True
    )
    
    print(f"Deleted {result['count']} resources")
    for rid in result['deleted']:
        print(f"  - {rid}")
```

## Multi-Cloud Support

Support for Azure Government and other sovereign clouds:

```bash
# Azure Government
mazure seed from-azure <tenant-id> --environment AZURE_GOVERNMENT

# Azure China
mazure seed from-azure <tenant-id> --environment AZURE_CHINA

# Azure Germany
mazure seed from-azure <tenant-id> --environment AZURE_GERMANY
```

## Troubleshooting

### Authentication Issues

```bash
# Verify Azure CLI authentication
az account show

# Verify service principal
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
```

### MongoDB Connection

Ensure MongoDB is running and accessible:

```bash
# Local MongoDB
mongod --dbpath /path/to/data

# Or use Docker
docker run -d -p 27017:27017 mongo
```

### Import Errors

If discovery commands are not available:

```bash
# Install required packages
pip install azure-discovery azure-identity

# Verify installation
python -c "import azure_discovery; print('OK')"
```

## Best Practices

### 1. Commit Snapshots to Version Control

Store snapshots in your repository for reproducible tests:

```bash
git add fixtures/*.json
git commit -m "Add test fixtures from production"
```

### 2. Update Snapshots Regularly

Schedule regular updates to keep test data fresh:

```bash
# Weekly cron job
0 2 * * 0 mazure seed from-azure <tenant-id> --output fixtures/weekly-snapshot.json
```

### 3. Use Separate Snapshots per Scenario

```
fixtures/
  ├── prod-baseline.json          # Full production topology
  ├── compute-only.json            # Just VMs and networking
  ├── entra-security.json          # Identity and security focused
  └── minimal-test.json            # Minimal resources for fast tests
```

### 4. Clear State Between Tests

Use pytest fixtures to ensure clean state:

```python
@pytest.fixture(autouse=True)
async def clean_state():
    from mazure.core.state import GenericResource
    from mazure.core.relationships import ResourceRelationship
    
    # Clear before test
    GenericResource.objects.delete()
    ResourceRelationship.objects.delete()
    
    yield
    
    # Clear after test
    GenericResource.objects.delete()
    ResourceRelationship.objects.delete()
```

## Next Steps

- **Phase 2**: Resource Graph query engine and Graph API mocks
- **Phase 3**: Response synthesis and validation framework
- **Phase 4**: Production hardening and performance optimization

See [AzureDiscoveryIntegrationPlan.md](../AzureDiscoveryIntegrationPlan.md) for the complete roadmap.

## References

- [AzureDiscovery Repository](https://github.com/maravedi/AzureDiscovery)
- [Azure Discovery Integration Plan](../AzureDiscoveryIntegrationPlan.md)
- [Mazure README](../README.md)
