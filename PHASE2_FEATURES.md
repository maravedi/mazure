# Phase 2 Features - Query Engine Implementation

**Status:** ✅ Core Implementation Complete  
**Date:** February 7, 2026  
**Branch:** azure-discovery-integration-plan

## Overview

This document describes the newly implemented query engine capabilities that enable testing Azure infrastructure and identity queries against discovery-seeded mock data.

---

## New Features

### 1. Azure Resource Graph Query Engine

**Location:** `mazure/services/resource_graph.py`

A complete KQL (Kusto Query Language) parser and execution engine for Azure Resource Graph queries.

#### Supported KQL Operators

- **WHERE** - Filter resources by type, location, name, tags
- **PROJECT** - Select specific fields to return
- **TAKE/LIMIT** - Limit number of results
- **EXTEND** - Add computed columns
- **SUMMARIZE** - Aggregate data (count by field)
- **ORDER BY** - Sort results ascending or descending

#### Supported Tables

- **Resources** - All ARM resources (VMs, storage, networks, etc.)
- **ResourceContainers** - Subscriptions and resource groups

#### Example Queries

```python
from mazure.services.resource_graph import ResourceGraphService
from mazure.core.state import StateManager

service = ResourceGraphService(StateManager())

# Find all VMs in East US
result = await service.query(
    subscriptions=['sub-id'],
    query="Resources | where type =~ 'Microsoft.Compute/virtualMachines' and location == 'eastus'"
)

# Count resources by type
result = await service.query(
    subscriptions=['sub-id'],
    query="Resources | summarize count() by type"
)

# Get VM names and locations only
result = await service.query(
    subscriptions=['sub-id'],
    query="Resources | where type =~ 'Microsoft.Compute/virtualMachines' | project name, location"
)
```

#### REST API Endpoint

**POST** `/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01`

```json
{
  "subscriptions": ["sub-id-1"],
  "query": "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | take 10",
  "options": {
    "$skip": 0,
    "$top": 100
  }
}
```

**Response:**
```json
{
  "totalRecords": 42,
  "count": 10,
  "data": [...],
  "facets": [],
  "resultTruncated": "false"
}
```

---

### 2. Microsoft Graph API Mock

**Location:** `mazure/services/graph.py`

Complete Microsoft Graph API v1.0 mock for Entra ID queries.

#### Supported Endpoints

##### Users

- **GET** `/v1.0/users` - List users
- **GET** `/v1.0/users/{id}` - Get user by ID or UPN

##### Groups

- **GET** `/v1.0/groups` - List groups
- **GET** `/v1.0/groups/{id}` - Get group by ID
- **GET** `/v1.0/groups/{id}/members` - List group members

#### Supported OData Parameters

- **$select** - Choose fields to return
- **$filter** - Filter results (eq, startswith, endswith, ne null)
- **$top** - Limit results (1-999)
- **$skip** - Skip results for pagination
- **$orderby** - Sort results (asc/desc)

#### Example Usage

```python
from mazure.services.graph import GraphService
from mazure.core.state import StateManager

service = GraphService(StateManager())

# List first 10 users
result = await service.list_users(top=10, skip=0)

# Find users by name
result = await service.list_users(
    filter_expr="startswith(displayName,'John')"
)

# Get specific user
result = await service.get_user('user-id-or-upn')

# Get group members
result = await service.list_group_members('group-id', top=50)
```

#### REST API Examples

**GET** `/v1.0/users?$top=10&$select=displayName,mail&$filter=startswith(displayName,'John')`

```json
{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
  "value": [
    {
      "id": "user-guid",
      "displayName": "John Doe",
      "mail": "john.doe@contoso.com"
    }
  ],
  "@odata.nextLink": "https://graph.microsoft.com/v1.0/users?$skip=10&$top=10"
}
```

**GET** `/v1.0/groups/{id}/members`

```json
{
  "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects",
  "value": [
    {
      "@odata.type": "#microsoft.graph.user",
      "id": "user-guid",
      "displayName": "Jane Smith",
      "userPrincipalName": "jane.smith@contoso.com"
    }
  ]
}
```

---

### 3. Response Synthesizer

**Location:** `mazure/codegen/response_synthesizer.py`

Generates realistic mock resources based on statistical patterns learned from discovery data.

#### Features

- **Pattern Analysis** - Learn from historical discovery snapshots
- **Location Distribution** - Use actual location frequencies per resource type
- **Tag Patterns** - Apply common tags with realistic values
- **Property Patterns** - Generate properties based on observed schemas
- **Batch Generation** - Create multiple resources at once

#### Example Usage

```python
from mazure.codegen.response_synthesizer import ResponseSynthesizer
from mazure.scenarios.snapshot_manager import SnapshotManager

# Load historical data
manager = SnapshotManager()
nodes, _ = await manager.load_snapshot('fixtures/prod-topology.json')

# Initialize synthesizer
synth = ResponseSynthesizer(nodes)

# Generate realistic VMs
vms = synth.synthesize_batch(
    resource_type='Microsoft.Compute/virtualMachines',
    count=5,
    override_tags={'environment': 'test'}
)

for vm in vms:
    print(f"{vm['name']} in {vm['location']}")
    print(f"  Properties: {list(vm['properties'].keys())}")
    print(f"  Tags: {vm['tags']}")

# Get statistics
stats = synth.get_statistics()
print(f"Learned patterns from {stats['total_resources']} resources")
print(f"Resource types: {len(stats['resource_types'])}")

# Get common patterns for a type
locations = synth.get_common_locations_for_type('Microsoft.Compute/virtualMachines')
tags = synth.get_common_tags_for_type('Microsoft.Compute/virtualMachines')
```

---

## Integration Guide

### Prerequisites

1. **MongoDB** - Running and accessible
2. **Discovery Data** - Seeded from live Azure or snapshot
3. **Mazure Package** - Installed and configured

### Step 1: Seed Data

```bash
# Seed from live Azure
mazure seed from-azure <tenant-id> \
  --subscription <sub-id> \
  --include-entra \
  --output fixtures/prod-topology.json

# Or load from existing snapshot
mazure snapshot load fixtures/prod-topology.json --clear
```

### Step 2: Register Routes

In your FastAPI application:

```python
from fastapi import FastAPI
from mazure.api.resource_graph_routes import router as rg_router
from mazure.api.graph_routes import router as graph_router

app = FastAPI()

# Register Resource Graph routes
app.include_router(rg_router)

# Register Microsoft Graph routes  
app.include_router(graph_router)
```

### Step 3: Query Data

```python
import httpx

# Query Resource Graph
response = httpx.post(
    "http://localhost:8000/providers/Microsoft.ResourceGraph/resources",
    json={
        "subscriptions": ["sub-id"],
        "query": "Resources | where type =~ 'Microsoft.Compute/virtualMachines'"
    }
)
resources = response.json()

# Query Graph API
response = httpx.get(
    "http://localhost:8000/v1.0/users",
    params={"$top": 10, "$filter": "startswith(displayName,'John')"}
)
users = response.json()
```

---

## Testing Integration

### Unit Tests

```python
import pytest
from mazure.services.resource_graph import ResourceGraphService
from mazure.services.graph import GraphService
from mazure.core.state import StateManager

@pytest.fixture
async def seeded_state():
    """Load test snapshot."""
    from mazure.scenarios.snapshot_manager import SnapshotManager
    manager = SnapshotManager()
    await manager.seed_from_snapshot(
        'fixtures/test-snapshot.json',
        StateManager(),
        clear_existing=True
    )

@pytest.mark.asyncio
async def test_resource_graph_query(seeded_state):
    service = ResourceGraphService(StateManager())
    result = await service.query(
        subscriptions=['test-sub'],
        query="Resources | where type =~ 'Microsoft.Compute/virtualMachines'"
    )
    assert result['count'] > 0
    assert 'data' in result

@pytest.mark.asyncio
async def test_graph_api_users(seeded_state):
    service = GraphService(StateManager())
    result = await service.list_users(top=10)
    assert 'value' in result
    assert '@odata.context' in result
```

### Integration Tests

```python
from fastapi.testclient import TestClient
from your_app import app

client = TestClient(app)

def test_resource_graph_endpoint():
    response = client.post(
        "/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01",
        json={
            "subscriptions": ["test-sub"],
            "query": "Resources | take 5"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert 'count' in data

def test_graph_api_endpoint():
    response = client.get(
        "/v1.0/users",
        params={"$top": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert 'value' in data
```

---

## Examples

See `examples/query_examples.py` for comprehensive examples including:

- Resource Graph query patterns
- Microsoft Graph API usage
- Snapshot workflow
- Response synthesis

**Run examples:**
```bash
python examples/query_examples.py
```

---

## Architecture

### Component Diagram

```
┌───────────────────────────┐
│ Azure Discovery          │
│ (Live Azure Queries)     │
└────────┬──────────────────┘
         │
         │ Discovery Data
         │
         ↓
┌────────┴──────────────────┐
│ DiscoveryStateSeeder       │
│ (Import to MongoDB)        │
└────────┬──────────────────┘
         │
         │ Seeded State
         │
         ↓
┌────────┴──────────────────────────────────────┐
│                MongoDB State Store                    │
│  - GenericResource collection                         │
│  - ResourceRelationship collection                    │
└────────┬────────────────┬───────────────────────┘
         │                   │
         ↓                   ↓
┌────────┴────────┐  ┌────────┴─────────┐
│ ResourceGraph   │  │ GraphService    │
│ Service         │  │ (Graph API)     │
└────────┬────────┘  └────────┬─────────┘
         │                   │
         │                   │
         ↓                   ↓
┌────────┴─────────────────────────────────┐
│         FastAPI REST Endpoints               │
│  - /providers/Microsoft.ResourceGraph/...  │
│  - /v1.0/users, /v1.0/groups, ...          │
└───────────────────────────────────────────┘
         │
         ↓
┌───────────────────────────────────────────┐
│        Test Suite / Applications            │
└───────────────────────────────────────────┘
```

### Data Flow

1. **Discovery** → Azure resources queried via AzureDiscovery
2. **Import** → Data seeded into MongoDB via DiscoveryStateSeeder
3. **Storage** → Resources and relationships stored in MongoDB
4. **Query** → Services query MongoDB using state manager
5. **Response** → FastAPI routes return formatted responses
6. **Test** → Test suites query endpoints for validation

---

## Performance Considerations

### Query Optimization

- **Indexes** - Create MongoDB indexes on commonly queried fields:
  ```javascript
  db.generic_resources.createIndex({"subscription_id": 1, "type": 1})
  db.generic_resources.createIndex({"location": 1})
  db.generic_resources.createIndex({"tags.environment": 1})
  ```

- **Pagination** - Always use $top and $skip for large result sets
- **Field Selection** - Use PROJECT or $select to limit returned data
- **Filtering** - Apply WHERE/$filter as early as possible

### Memory Usage

- Large snapshots (1000+ resources) may take several seconds to load
- Consider splitting snapshots by subscription or resource type
- Use lazy loading for relationship expansion

---

## Troubleshooting

### MongoDB Connection Issues

```python
# Check MongoDB connection
from mongoengine import connect
connect('mazure', host='localhost', port=27017)
```

### No Results Returned

1. Verify data is seeded:
   ```bash
   mazure snapshot list
   ```

2. Check MongoDB:
   ```javascript
   db.generic_resources.count()
   db.resource_relationships.count()
   ```

3. Verify query syntax:
   ```python
   # Start with simple query
   result = await service.query(['sub-id'], 'Resources | take 5')
   ```

### Filter Not Working

- Check case sensitivity (use =~ for case-insensitive)
- Verify field names match discovered data
- Test with simpler queries first

---

## Next Steps

1. **Register Routes** - Add to your FastAPI application
2. **Write Tests** - Create integration tests for your use cases
3. **Seed Production Data** - Create realistic snapshots
4. **Explore Patterns** - Use ResponseSynthesizer for test data
5. **Extend Queries** - Add custom KQL operators as needed

---

## Support

For issues and questions:
- Review `IMPLEMENTATION_STATUS.md` for current status
- Check `examples/query_examples.py` for usage patterns
- See `AzureDiscoveryIntegrationPlan.md` for architecture details

---

## License

Same as mazure project
