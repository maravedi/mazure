# Azure Discovery Integration - User Guide

This guide explains how to use the Azure Discovery integration features in mazure to create realistic, data-driven mock environments for testing.

## Overview

The Azure Discovery integration allows you to:

1. **Seed mock state** from live Azure environments using AzureDiscovery
2. **Query infrastructure** using Resource Graph KQL queries
3. **Query identity data** using Microsoft Graph API
4. **Generate realistic test data** based on discovered patterns
5. **Validate dependencies** and perform cascading operations
6. **Generate schemas** automatically from discovered resources

## Quick Start

### 1. Seed Data from Azure

```bash
# Seed from live Azure tenant
mazure seed from-azure <tenant-id> \
  --subscription <sub-id> \
  --include-entra \
  --output fixtures/my-snapshot.json
```

### 2. Load Snapshot for Testing

```bash
# Load snapshot into mock state
mazure snapshot load fixtures/my-snapshot.json --clear
```

### 3. Query with Resource Graph

```python
from mazure.services.resource_graph import ResourceGraphService
from mazure.core.state import StateManager

service = ResourceGraphService(StateManager())

# KQL query
query = "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | take 10"
result = await service.query(["subscription-id"], query)

for vm in result['data']:
    print(f"VM: {vm['name']} in {vm['location']}")
```

### 4. Query with Graph API

```python
from mazure.services.graph import GraphService
from mazure.core.state import StateManager

service = GraphService(StateManager())

# List users
users = await service.list_users(top=10)
for user in users['value']:
    print(f"User: {user['displayName']} - {user['userPrincipalName']}")

# Get group members
members = await service.list_group_members(group_id, top=20)
```

## Features

### Resource Graph Query Engine

The Resource Graph service supports KQL queries:

#### Supported Operators

- **WHERE** - Filter resources
  ```kql
  Resources | where type =~ 'Microsoft.Compute/virtualMachines'
  Resources | where location == 'eastus'
  Resources | where name contains 'prod'
  Resources | where tags['environment'] == 'production'
  ```

- **PROJECT** - Select specific fields
  ```kql
  Resources | project name, type, location
  Resources | project name, properties.vmSize
  ```

- **TAKE/LIMIT** - Limit results
  ```kql
  Resources | take 10
  ```

- **EXTEND** - Add computed fields
  ```kql
  Resources | extend env = tags['environment']
  Resources | extend vmSize = properties.hardwareProfile.vmSize
  ```

- **SUMMARIZE** - Aggregate data
  ```kql
  Resources | summarize count() by type
  Resources | summarize count() by location
  ```

- **ORDER BY** - Sort results
  ```kql
  Resources | order by name asc
  Resources | order by location desc
  ```

#### Query Examples

```python
# Find all VMs in a specific location
query = """
    Resources 
    | where type =~ 'Microsoft.Compute/virtualMachines'
    | where location == 'eastus'
    | project name, properties.hardwareProfile.vmSize
"""

# Count resources by type
query = "Resources | summarize count() by type"

# Find resources with specific tag
query = """
    Resources 
    | where tags['environment'] == 'production'
    | take 20
"""

# Complex query with multiple operators
query = """
    Resources
    | where type =~ 'Microsoft.Network/virtualNetworks'
    | extend addressSpace = properties.addressSpace
    | project name, location, addressSpace
    | order by name asc
"""
```

### Microsoft Graph API

The Graph service implements v1.0 endpoints:

#### User Endpoints

```python
service = GraphService(StateManager())

# List users with OData parameters
result = await service.list_users(
    top=100,
    skip=0,
    select=['displayName', 'mail', 'department'],
    filter_expr="startswith(displayName, 'John')",
    orderby="displayName asc"
)

# Get specific user
user = await service.get_user("user-id-or-upn")
```

#### Group Endpoints

```python
# List groups
groups = await service.list_groups(
    top=50,
    filter_expr="securityEnabled eq true"
)

# Get group details
group = await service.get_group("group-id")

# List group members (uses relationships)
members = await service.list_group_members(
    "group-id",
    top=100
)
```

#### OData Query Parameters

- **$select** - Choose fields to return
- **$filter** - Filter results (supports: eq, ne, startswith, endswith)
- **$top** - Limit number of results
- **$skip** - Skip results for pagination
- **$orderby** - Sort results (asc/desc)

### Response Synthesizer

Generate realistic resources based on learned patterns:

```python
from mazure.codegen.response_synthesizer import ResponseSynthesizerFactory

# Create from snapshot
synth = ResponseSynthesizerFactory.from_snapshot('fixtures/prod.json')

# Generate single resource
vm = synth.synthesize_resource(
    resource_type='Microsoft.Compute/virtualMachines',
    name='test-vm-001',
    location='eastus',
    override_tags={'environment': 'test'}
)

# Generate batch
vms = synth.synthesize_batch(
    resource_type='Microsoft.Compute/virtualMachines',
    count=10,
    override_tags={'environment': 'staging'}
)

# View statistics
stats = synth.get_statistics()
print(f"Learned from {stats['total_resources']} resources")
print(f"Resource types: {stats['resource_types'].keys()}")
```

### Schema Generator

Automatically generate Pydantic schemas:

```python
from mazure.codegen.schema_generator import SchemaGeneratorFactory

# Generate schemas from snapshot
schemas = SchemaGeneratorFactory.from_snapshot(
    snapshot_path='fixtures/prod.json',
    output_dir='mazure/schemas/generated',
    min_samples=3
)

# Schemas are written to Python modules
# and can be imported:
# from mazure.schemas.generated.microsoft_compute_schemas import MicrosoftComputeVirtualMachinesProperties
```

### Relationship Engine

Handle cascading operations and dependencies:

```python
from mazure.core.relationship_engine import RelationshipEngine
from mazure.core.state import StateManager

engine = RelationshipEngine(StateManager())

# Analyze impact of deletion (dry run)
impact = await engine.delete_with_dependents(
    resource_id='/subscriptions/.../resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1',
    cascade=True,
    dry_run=True
)

print(f"Would delete {impact['count']} resources:")
for rid in impact['would_delete']:
    print(f"  - {rid}")

# Actually delete with cascade
result = await engine.delete_with_dependents(
    resource_id=resource_id,
    cascade=True,
    dry_run=False
)

# Validate dependencies before creation
validation = await engine.validate_create(
    resource_type='Microsoft.Compute/virtualMachines',
    properties=vm_properties
)

if not validation['valid']:
    print("Validation errors:")
    for error in validation['errors']:
        print(f"  - {error}")

# Get dependency tree
tree = await engine.get_resource_dependencies(
    resource_id=resource_id,
    depth=2,
    include_dependents=True
)
```

## Integration with FastAPI

The services are exposed via FastAPI routes:

### Resource Graph Endpoint

```python
from mazure.api.resource_graph_routes import router as rg_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(rg_router)

# Now available at:
# POST /providers/Microsoft.ResourceGraph/resources
```

**Example Request:**

```bash
curl -X POST http://localhost:8000/providers/Microsoft.ResourceGraph/resources \
  -H "Content-Type: application/json" \
  -d '{
    "subscriptions": ["sub-id"],
    "query": "Resources | where type =~ '"'"'Microsoft.Compute/virtualMachines'"'"' | take 10",
    "options": {"$skip": 0, "$top": 100}
  }'
```

### Graph API Endpoints

```python
from mazure.api.graph_routes import router as graph_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(graph_router)

# Now available at:
# GET /v1.0/users
# GET /v1.0/users/{id}
# GET /v1.0/groups
# GET /v1.0/groups/{id}
# GET /v1.0/groups/{id}/members
```

**Example Requests:**

```bash
# List users
curl http://localhost:8000/v1.0/users?\$top=10&\$select=displayName,mail

# Get specific user
curl http://localhost:8000/v1.0/users/user-id

# List group members
curl http://localhost:8000/v1.0/groups/group-id/members
```

## Testing Patterns

### Fixture-Based Testing

```python
import pytest
from pathlib import Path
from mazure.scenarios.snapshot_manager import SnapshotManager
from mazure.core.state import StateManager

@pytest.fixture(scope='session')
async def mock_azure_environment():
    """Load production-like Azure topology for tests."""
    snapshot_path = Path('fixtures/prod-topology.json')
    
    manager = SnapshotManager()
    state = StateManager()
    
    await manager.seed_from_snapshot(
        snapshot_path,
        state,
        clear_existing=True
    )
    
    yield state
    
    # Cleanup
    from mazure.core.state import GenericResource
    GenericResource.objects.delete()

@pytest.mark.usefixtures('mock_azure_environment')
def test_query_vms():
    """Test VM queries against seeded data."""
    service = ResourceGraphService(StateManager())
    
    result = await service.query(
        ['test-sub'],
        "Resources | where type =~ 'Microsoft.Compute/virtualMachines'"
    )
    
    assert len(result['data']) > 0
```

### Parametrized Testing with Snapshots

```python
@pytest.mark.parametrize('snapshot', [
    'fixtures/dev-topology.json',
    'fixtures/staging-topology.json',
    'fixtures/prod-topology.json'
])
def test_multi_environment(snapshot):
    """Test against multiple environment snapshots."""
    manager = SnapshotManager()
    nodes, rels = manager.load_snapshot(Path(snapshot))
    
    # Assertions based on snapshot
    assert len(nodes) > 0
```

## Best Practices

### 1. Snapshot Management

- **Version control snapshots**: Commit snapshots to git for reproducible tests
- **Update regularly**: Refresh snapshots weekly from production
- **Multiple environments**: Create separate snapshots for dev, staging, prod
- **Minimal snapshots**: Keep test snapshots small and focused

### 2. Query Performance

- **Use filters early**: Apply WHERE clauses before other operators
- **Limit results**: Use TAKE to avoid processing unnecessary data
- **Project only needed fields**: Reduce data transfer with PROJECT

### 3. Testing Strategy

- **Integration tests**: Use real snapshots for integration tests
- **Unit tests**: Use synthesized data for unit tests
- **CI/CD**: Load snapshots in CI for consistent test environment
- **Isolation**: Clear state between test runs

### 4. Development Workflow

```bash
# 1. Discover and snapshot
mazure seed from-azure <tenant> -s <sub> --output fixtures/latest.json

# 2. Load for development
mazure snapshot load fixtures/latest.json --clear

# 3. Run tests
pytest tests/integration/

# 4. Generate schemas (optional)
mazure codegen schemas --snapshot fixtures/latest.json --output mazure/schemas/
```

## Troubleshooting

### No Data Returned from Queries

- Ensure snapshot is loaded: `mazure snapshot list`
- Check subscription IDs match
- Verify MongoDB is running
- Check query syntax

### Authentication Errors During Seeding

- Ensure Azure CLI is logged in: `az login`
- Verify tenant ID is correct
- Check subscription access permissions

### Relationship Queries Return Empty

- Ensure discovery included `--include-entra`
- Verify relationships were imported
- Check relationship types in database

## Advanced Topics

### Custom Snapshot Transformations

```python
from mazure.scenarios.snapshot_manager import SnapshotManager

manager = SnapshotManager()
nodes, rels = manager.load_snapshot(Path('fixtures/prod.json'))

# Filter to specific resource types
filtered_nodes = [n for n in nodes if n.type == 'Microsoft.Compute/virtualMachines']

# Export filtered snapshot
manager.export_snapshot(
    filtered_nodes,
    rels,
    Path('fixtures/vms-only.json')
)
```

### Extending Query Support

To add new KQL operators, extend `ResourceGraphService._apply_query_operators()`:

```python
def _apply_query_operators(self, resources, query):
    # ... existing operators ...
    
    elif stage.lower().startswith('distinct'):
        field = stage[8:].strip()
        resources = self._apply_distinct(resources, field)
    
    return resources
```

## API Reference

See individual module documentation:

- [ResourceGraphService](../mazure/services/resource_graph.py)
- [GraphService](../mazure/services/graph.py)
- [ResponseSynthesizer](../mazure/codegen/response_synthesizer.py)
- [SchemaGenerator](../mazure/codegen/schema_generator.py)
- [RelationshipEngine](../mazure/core/relationship_engine.py)

## Examples

See `tests/integration/` for complete working examples.
