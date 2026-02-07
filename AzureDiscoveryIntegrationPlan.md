# Azure Discovery Integration Plan for Mazure

## Executive Summary

This document provides comprehensive technical recommendations for integrating [AzureDiscovery](https://github.com/maravedi/AzureDiscovery) capabilities into mazure to create a robust, self-updating mocking suite that accurately reflects real Azure environments without requiring live API access during testing.

**Key Objectives:**
- Automatically seed mazure state from live Azure topology discovery
- Generate realistic mock responses based on actual Azure resource patterns
- Maintain API compatibility through discovery-driven validation
- Enable topology-aware testing with relationship modeling
- Provide deterministic test scenarios via snapshot fixtures

---

## Architecture Overview

### Current State

**AzureDiscovery** (`entra-discovery-579955906606419153` branch) is a sophisticated tenant discovery tool that:
- Queries Azure Resource Graph (ARM) for infrastructure resources
- Enumerates Entra ID objects via Microsoft Graph API
- Produces normalized `ResourceNode` and `ResourceRelationship` Pydantic models
- Supports all Azure clouds (Public, Government, China, Germany)
- Implements bounded relationship expansion with configurable limits
- Generates interactive PyVis dependency graphs

**Mazure** (master branch) is an Azure mocking framework that:
- Provides Moto-like decorators and context managers for Azure
- Uses MongoDB for state management via `GenericResource` model
- Implements basic ARM services (Compute, Storage, Network)
- Includes AutoRest-based code generation (planned)
- Offers CLI for service generation and mock server

### Integration Vision

Transform mazure from a manually-maintained mock framework into an intelligent, discovery-driven testing suite where:
1. Real Azure topologies seed mock state
2. Actual resource structures inform response schemas
3. Relationship data enables dependency-aware operations
4. Continuous discovery keeps mocks synchronized with Azure API evolution
5. Snapshot fixtures provide reproducible test environments

---

## Core Technical Recommendations

### 1. Discovery-to-Mock State Seeding Pipeline

**Objective:** Create a bidirectional integration where AzureDiscovery's enumeration output directly seeds mazure's mock state.

#### Implementation

```python
# mazure/seeding/discovery_importer.py
from typing import List, Dict, Any
from azure_discovery import AzureDiscoveryRequest, AzureDiscoveryResponse, run_discovery
from ..core.state import StateManager, GenericResource

class DiscoveryStateSeeder:
    """Import AzureDiscovery enumeration results into mazure state"""
    
    def __init__(self, state_manager: StateManager):
        self.state = state_manager
    
    async def seed_from_discovery(
        self,
        discovery_request: AzureDiscoveryRequest
    ) -> Dict[str, int]:
        """Execute discovery and populate mock state with real topology"""
        
        # Run discovery against live Azure
        response: AzureDiscoveryResponse = await run_discovery(discovery_request)
        
        stats = {
            'arm_resources': 0,
            'entra_objects': 0,
            'relationships': 0
        }
        
        # Import ARM resources
        for node in response.nodes:
            if not node.id.startswith('graph://'):
                # ARM resource
                await self._import_arm_resource(node)
                stats['arm_resources'] += 1
            else:
                # Entra/Graph resource
                await self._import_graph_object(node)
                stats['entra_objects'] += 1
        
        # Import relationships for dependency modeling
        for rel in response.relationships:
            await self._import_relationship(rel)
            stats['relationships'] += 1
        
        return stats
    
    async def _import_arm_resource(self, node) -> GenericResource:
        """Convert ResourceNode to GenericResource"""
        
        # Parse Azure resource ID
        parts = node.id.split('/')
        provider_idx = parts.index('providers') if 'providers' in parts else None
        
        if provider_idx:
            resource_type = f"{parts[provider_idx + 1]}/{parts[provider_idx + 2]}"
            resource_name = parts[-1]
            resource_group = parts[parts.index('resourceGroups') + 1]
            subscription_id = parts[parts.index('subscriptions') + 1]
        else:
            # Fallback parsing
            resource_type = node.type
            resource_name = node.name
            resource_group = node.resource_group or 'default-rg'
            subscription_id = node.subscription_id
        
        return await self.state.create_resource(
            resource_type=resource_type,
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=resource_name,
            properties=node.properties or {},
            location=node.location or 'eastus',
            tags=node.tags or {},
            resource_id=node.id,
            # Preserve all discovery metadata
            _discovery_metadata={
                'discovered_at': node.tags.get('_discovery_timestamp'),
                'tenant_id': node.tags.get('_tenant_id'),
                'kind': node.kind
            }
        )
    
    async def _import_graph_object(self, node):
        """Import Entra ID Graph objects as special resource types"""
        
        # Store Graph objects as pseudo-resources for query support
        return await self.state.create_resource(
            resource_type=node.type,
            subscription_id='Tenant',
            resource_group='EntraID',
            name=node.name,
            properties=node.properties or {},
            location='global',
            tags=node.tags or {},
            resource_id=node.id
        )
    
    async def _import_relationship(self, rel):
        """Store relationship edges for graph queries"""
        
        # Store in separate collection for Resource Graph query support
        from ..core.relationships import ResourceRelationship as MazureRel
        
        return await MazureRel.create(
            source_id=rel.source_id,
            target_id=rel.target_id,
            relation_type=rel.relation_type,
            weight=rel.weight
        )
```

#### CLI Integration

```python
# mazure/cli/seed.py
import typer
from typing import List, Optional
from pathlib import Path

app = typer.Typer()

@app.command()
async def from_azure(
    tenant_id: str = typer.Argument(..., help="Azure tenant ID"),
    subscription: List[str] = typer.Option(None, "--subscription", "-s", help="Subscription IDs to discover"),
    include_entra: bool = typer.Option(True, help="Include Entra ID objects"),
    output_snapshot: Optional[Path] = typer.Option(None, "--output", help="Save snapshot to file")
):
    """Seed mazure state from live Azure environment"""
    
    from azure_discovery import AzureDiscoveryRequest, AzureEnvironment
    from ..seeding.discovery_importer import DiscoveryStateSeeder
    from ..core.state import StateManager
    
    request = AzureDiscoveryRequest(
        tenant_id=tenant_id,
        environment=AzureEnvironment.AZURE_PUBLIC,
        subscriptions=subscription or [],
        include_entra=include_entra,
        include_relationships=True
    )
    
    seeder = DiscoveryStateSeeder(StateManager())
    stats = await seeder.seed_from_discovery(request)
    
    typer.echo(f"✓ Seeded {stats['arm_resources']} ARM resources")
    typer.echo(f"✓ Seeded {stats['entra_objects']} Entra objects")
    typer.echo(f"✓ Created {stats['relationships']} relationships")
    
    if output_snapshot:
        # Export snapshot for version control/sharing
        await seeder.export_snapshot(output_snapshot)
        typer.echo(f"✓ Snapshot saved to {output_snapshot}")
```

**Usage:**
```bash
# Seed from live Azure
mazure seed from-azure <tenant-id> -s <sub-id-1> -s <sub-id-2> --include-entra

# Export snapshot for test fixtures
mazure seed from-azure <tenant-id> --output fixtures/prod-topology.json
```

---

### 2. Pydantic Schema Generation from Discovery Models

**Objective:** Leverage AzureDiscovery's Pydantic models to generate mazure's response schemas automatically.

#### Implementation

```python
# mazure/codegen/schema_generator.py
from typing import Type, List, Dict, Any, get_type_hints
from pydantic import BaseModel, create_model, Field
from azure_discovery.adt_types import ResourceNode
from collections import defaultdict

class SchemaGenerator:
    """Generate Pydantic schemas from discovery models"""
    
    def generate_resource_schema(
        self,
        resource_type: str,
        sample_nodes: List[ResourceNode],
        min_coverage: float = 0.5
    ) -> Type[BaseModel]:
        """Infer Pydantic schema from discovered resource samples
        
        Args:
            resource_type: Azure resource type (e.g., 'Microsoft.Compute/virtualMachines')
            sample_nodes: List of ResourceNode samples from discovery
            min_coverage: Minimum percentage of samples that must contain a field
        
        Returns:
            Dynamically generated Pydantic model class
        """
        
        if not sample_nodes:
            raise ValueError(f"No samples provided for {resource_type}")
        
        # Aggregate property statistics from samples
        property_stats = defaultdict(lambda: {'types': [], 'count': 0})
        
        for node in sample_nodes:
            if node.type == resource_type and node.properties:
                for key, value in node.properties.items():
                    property_stats[key]['types'].append(type(value))
                    property_stats[key]['count'] += 1
        
        # Build field definitions
        fields = {}
        for prop_name, stats in property_stats.items():
            # Include field if it appears in min_coverage% of samples
            if stats['count'] / len(sample_nodes) >= min_coverage:
                field_type = self._infer_type(stats['types'])
                fields[prop_name] = (field_type, Field(default=None))
        
        # Generate dynamic Pydantic model
        schema_name = resource_type.replace('/', '_').replace('.', '_') + '_Properties'
        return create_model(schema_name, **fields)
    
    def _infer_type(self, type_samples: List[type]) -> type:
        """Infer Python type from sample values
        
        Handles type conflicts by choosing most specific common type.
        """
        from collections import Counter
        
        type_counts = Counter(type_samples)
        most_common_type = type_counts.most_common(1)[0][0]
        
        # Type mapping
        if most_common_type == bool:
            return bool
        elif most_common_type == int:
            # Could be int or float if mixed
            if float in type_counts:
                return float
            return int
        elif most_common_type == float:
            return float
        elif most_common_type == list:
            return List[Any]
        elif most_common_type == dict:
            return Dict[str, Any]
        else:
            return str
    
    def generate_all_schemas(
        self,
        nodes: List[ResourceNode],
        output_dir: Path
    ):
        """Generate schema modules for all discovered resource types"""
        
        # Group nodes by type
        by_type = defaultdict(list)
        for node in nodes:
            if not node.id.startswith('graph://'):
                by_type[node.type].append(node)
        
        # Generate schema for each type
        for resource_type, samples in by_type.items():
            if len(samples) < 3:  # Need at least 3 samples
                continue
            
            schema = self.generate_resource_schema(resource_type, samples)
            
            # Write to module
            provider = resource_type.split('/')[0].replace('.', '_').lower()
            module_path = output_dir / f"{provider}_schemas.py"
            
            self._write_schema_module(module_path, resource_type, schema)
    
    def _write_schema_module(self, path: Path, resource_type: str, schema: Type[BaseModel]):
        """Write Pydantic schema to Python module"""
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'a') as f:
            f.write(f"\n# {resource_type}\n")
            f.write(f"class {schema.__name__}(BaseModel):\n")
            for field_name, field_info in schema.__fields__.items():
                f.write(f"    {field_name}: {field_info.annotation}\n")
```

**CLI Command:**
```bash
# Generate schemas from discovery snapshot
mazure codegen schemas --snapshot fixtures/prod-topology.json --output mazure/schemas/
```

---

### 3. Resource Graph Query Engine Integration

**Objective:** Implement mazure's Resource Graph endpoint using discovery relationship data to support KQL-style queries.

#### Implementation

```python
# mazure/services/resource_graph.py
from typing import List, Dict, Any, Optional
import re
from ..core.state import StateManager, GenericResource

class ResourceGraphService:
    """Mock Azure Resource Graph queries using seeded state"""
    
    def __init__(self, state: StateManager):
        self.state = state
    
    async def query(
        self,
        subscriptions: List[str],
        query: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute KQL-style Resource Graph query against mock state
        
        Supports basic KQL operators:
        - Resources | where type =~ 'resourceType'
        - Resources | project name, type, location
        - Resources | take 10
        - Resources | extend custom = properties.customField
        """
        
        # Parse query type (Resources, ResourceContainers, etc.)
        if query.strip().startswith('Resources'):
            resources = await self._query_resources(subscriptions, query)
        elif query.strip().startswith('ResourceContainers'):
            resources = await self._query_containers(subscriptions, query)
        else:
            raise ValueError(f"Unsupported query table: {query.split()[0]}")
        
        # Apply KQL operators
        resources = await self._apply_query_operators(resources, query)
        
        return {
            'totalRecords': len(resources),
            'count': len(resources),
            'data': resources,
            'facets': [],
            'resultTruncated': 'false'
        }
    
    async def _query_resources(
        self,
        subscriptions: List[str],
        query: str
    ) -> List[Dict[str, Any]]:
        """Query Resources table (all ARM resources)"""
        
        all_resources = []
        for sub_id in subscriptions:
            # Get all resource types for subscription
            # In real implementation, query MongoDB directly
            from mongoengine import Q
            resources = GenericResource.objects(
                Q(subscription_id=sub_id) & ~Q(resource_group='EntraID')
            )
            all_resources.extend([r.to_arm_dict() for r in resources])
        
        return all_resources
    
    async def _query_containers(
        self,
        subscriptions: List[str],
        query: str
    ) -> List[Dict[str, Any]]:
        """Query ResourceContainers (subscriptions and resource groups)"""
        
        containers = []
        for sub_id in subscriptions:
            # Add subscription container
            containers.append({
                'id': f'/subscriptions/{sub_id}',
                'name': sub_id,
                'type': 'microsoft.resources/subscriptions',
                'tenantId': 'mock-tenant-id'
            })
            
            # Add resource groups
            rg_names = GenericResource.objects(
                subscription_id=sub_id
            ).distinct('resource_group')
            
            for rg_name in rg_names:
                if rg_name != 'EntraID':  # Skip Graph pseudo-RG
                    containers.append({
                        'id': f'/subscriptions/{sub_id}/resourceGroups/{rg_name}',
                        'name': rg_name,
                        'type': 'microsoft.resources/resourcegroups',
                        'location': 'eastus'
                    })
        
        return containers
    
    async def _apply_query_operators(
        self,
        resources: List[Dict],
        query: str
    ) -> List[Dict]:
        """Apply KQL operators: where, project, take, extend, etc."""
        
        # Split query into pipeline stages
        stages = [s.strip() for s in query.split('|')]
        
        for stage in stages[1:]:  # Skip table name
            if stage.lower().startswith('where'):
                condition = stage[5:].strip()
                resources = self._filter_where(resources, condition)
            
            elif stage.lower().startswith('project'):
                fields_str = stage[7:].strip()
                fields = [f.strip() for f in fields_str.split(',')]
                resources = self._project_fields(resources, fields)
            
            elif stage.lower().startswith('take') or stage.lower().startswith('limit'):
                match = re.search(r'\d+', stage)
                if match:
                    limit = int(match.group())
                    resources = resources[:limit]
            
            elif stage.lower().startswith('extend'):
                resources = self._apply_extend(resources, stage[6:].strip())
            
            elif stage.lower().startswith('summarize'):
                resources = self._apply_summarize(resources, stage[9:].strip())
        
        return resources
    
    def _filter_where(self, resources: List[Dict], condition: str) -> List[Dict]:
        """Apply WHERE filter (simplified KQL implementation)
        
        Supports:
        - type =~ 'resourceType' (case-insensitive)
        - type == 'resourceType' (case-sensitive)
        - location == 'eastus'
        - tags['environment'] == 'prod'
        - name contains 'substring'
        """
        
        # Type filter (case-insensitive)
        match = re.search(r"type\s*=~\s*['\"](.+?)['\"]|", condition)
        if match:
            resource_type = match.group(1).lower()
            return [r for r in resources if r.get('type', '').lower() == resource_type]
        
        # Type filter (case-sensitive)
        match = re.search(r"type\s*==\s*['\"](.+?)['\"]|", condition)
        if match:
            resource_type = match.group(1)
            return [r for r in resources if r.get('type') == resource_type]
        
        # Location filter
        match = re.search(r"location\s*==\s*['\"](.+?)['\"]|", condition)
        if match:
            location = match.group(1)
            return [r for r in resources if r.get('location') == location]
        
        # Name contains
        match = re.search(r"name\s+contains\s+['\"](.+?)['\"]|", condition, re.IGNORECASE)
        if match:
            substring = match.group(1)
            return [r for r in resources if substring in r.get('name', '')]
        
        # Tag filter
        match = re.search(r"tags\\[['\"](\w+)['\"]\\]\s*==\s*['\"](.+?)['\"]|", condition)
        if match:
            tag_key, tag_value = match.groups()
            return [r for r in resources if r.get('tags', {}).get(tag_key) == tag_value]
        
        # If no pattern matches, return all (safe default)
        return resources
    
    def _project_fields(self, resources: List[Dict], fields: List[str]) -> List[Dict]:
        """Project specific fields (SELECT equivalent)"""
        
        projected = []
        for r in resources:
            proj = {}
            for field in fields:
                # Handle nested properties: properties.field
                if '.' in field:
                    parts = field.split('.')
                    value = r
                    for part in parts:
                        value = value.get(part, {}) if isinstance(value, dict) else None
                    proj[field] = value
                else:
                    proj[field] = r.get(field)
            projected.append(proj)
        
        return projected
    
    def _apply_extend(self, resources: List[Dict], expression: str) -> List[Dict]:
        """Add computed columns (EXTEND operator)
        
        Example: extend env = tags['environment']
        """
        
        # Parse: newField = expression
        match = re.match(r"(\w+)\s*=\s*(.+)", expression)
        if not match:
            return resources
        
        new_field, expr = match.groups()
        
        for r in resources:
            # Simple tag extraction
            tag_match = re.search(r"tags\\[['\"](\w+)['\"]\\]|", expr)
            if tag_match:
                tag_key = tag_match.group(1)
                r[new_field] = r.get('tags', {}).get(tag_key)
            # Could add more expression types
        
        return resources
    
    def _apply_summarize(self, resources: List[Dict], expression: str) -> List[Dict]:
        """Aggregate data (SUMMARIZE operator)
        
        Example: summarize count() by type
        """
        
        # Simple count by field
        match = re.match(r"count\\(\\)\s+by\s+(\w+)", expression)
        if match:
            group_field = match.group(1)
            from collections import Counter
            counts = Counter(r.get(group_field) for r in resources)
            return [
                {group_field: key, 'count': count}
                for key, count in counts.items()
            ]
        
        return resources
```

**FastAPI Route:**
```python
# mazure/api/resource_graph.py
from fastapi import APIRouter, Depends, Body
from typing import List, Dict, Any
from ..services.resource_graph import ResourceGraphService
from ..core.state import StateManager

router = APIRouter(prefix="/providers/Microsoft.ResourceGraph")

@router.post("/resources")
async def query_resources(
    payload: Dict[str, Any] = Body(...),
    service: ResourceGraphService = Depends(lambda: ResourceGraphService(StateManager()))
):
    """Azure Resource Graph query endpoint
    
    POST /providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01
    Body: {
        "subscriptions": ["sub-id-1"],
        "query": "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | take 10"
    }
    """
    
    subscriptions = payload.get('subscriptions', [])
    query = payload.get('query', 'Resources')
    options = payload.get('options', {})
    
    return await service.query(subscriptions, query, options)
```

---

### 4. Microsoft Graph API Mock Layer

**Objective:** Implement Graph API endpoints using discovered Entra data to support identity and directory queries.

#### Implementation

```python
# mazure/services/graph.py
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from ..core.state import StateManager, GenericResource

router = APIRouter(prefix="/v1.0")

class GraphService:
    """Microsoft Graph API mock using Entra discovery data"""
    
    def __init__(self, state: StateManager):
        self.state = state
    
    async def list_users(
        self,
        top: int = 100,
        skip: int = 0,
        select: Optional[List[str]] = None,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/users endpoint"""
        
        # Query users seeded from Entra discovery
        query_params = {
            'subscription_id': 'Tenant',
            'resource_group': 'EntraID',
            'resource_type': 'Microsoft.Graph/User'
        }
        
        users = GenericResource.objects(**query_params)
        
        # Apply $filter (simplified)
        if filter_expr:
            users = self._apply_odata_filter(users, filter_expr)
        
        # Count before pagination
        total = users.count()
        
        # Apply pagination
        paginated = list(users.skip(skip).limit(top))
        
        # Format as Graph API response
        value = [self._format_graph_user(u, select) for u in paginated]
        
        response = {
            '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#users',
            'value': value
        }
        
        # Add next link if more results
        if skip + top < total:
            response['@odata.nextLink'] = f'/v1.0/users?$skip={skip + top}&$top={top}'
        
        return response
    
    async def get_user(
        self,
        user_id: str,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/users/{id} endpoint"""
        
        # Find by graph ID in tags or resource_id
        user = GenericResource.objects(
            resource_type='Microsoft.Graph/User',
            resource_id__icontains=user_id
        ).first()
        
        if not user:
            # Try by UPN in name
            user = GenericResource.objects(
                resource_type='Microsoft.Graph/User',
                name=user_id
            ).first()
        
        if not user:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="User not found")
        
        return self._format_graph_user(user, select)
    
    async def list_groups(
        self,
        top: int = 100,
        skip: int = 0,
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/groups endpoint"""
        
        groups = GenericResource.objects(
            subscription_id='Tenant',
            resource_group='EntraID',
            resource_type='Microsoft.Graph/Group'
        )
        
        if filter_expr:
            groups = self._apply_odata_filter(groups, filter_expr)
        
        total = groups.count()
        paginated = list(groups.skip(skip).limit(top))
        
        response = {
            '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#groups',
            'value': [self._format_graph_group(g) for g in paginated]
        }
        
        if skip + top < total:
            response['@odata.nextLink'] = f'/v1.0/groups?$skip={skip + top}'
        
        return response
    
    async def list_group_members(
        self,
        group_id: str,
        top: int = 100
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/groups/{id}/members endpoint
        
        Uses relationships stored during discovery import.
        """
        
        from ..core.relationships import ResourceRelationship
        
        # Find group node
        group_resource_id = f"graph://group/{group_id}"
        
        # Get member relationships
        member_rels = ResourceRelationship.objects(
            source_id=group_resource_id,
            relation_type='has_member'
        ).limit(top)
        
        # Load member objects
        members = []
        for rel in member_rels:
            member = GenericResource.objects(resource_id=rel.target_id).first()
            if member:
                members.append(self._format_directory_object(member))
        
        return {
            '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#directoryObjects',
            'value': members
        }
    
    def _format_graph_user(self, resource: GenericResource, select: Optional[List[str]] = None) -> Dict:
        """Format GenericResource as Graph API user object"""
        
        props = resource.properties or {}
        graph_id = resource.tags.get('graph_id', 'unknown')
        
        user = {
            'id': graph_id,
            'userPrincipalName': props.get('userPrincipalName', resource.name),
            'displayName': props.get('displayName', resource.name),
            'givenName': props.get('givenName'),
            'surname': props.get('surname'),
            'mail': props.get('mail'),
            'jobTitle': props.get('jobTitle'),
            'department': props.get('department'),
            'officeLocation': props.get('officeLocation'),
            'mobilePhone': props.get('mobilePhone'),
            'accountEnabled': props.get('accountEnabled', True)
        }
        
        # Apply $select if provided
        if select:
            user = {k: v for k, v in user.items() if k in select or k == 'id'}
        
        return user
    
    def _format_graph_group(self, resource: GenericResource) -> Dict:
        """Format GenericResource as Graph API group object"""
        
        props = resource.properties or {}
        graph_id = resource.tags.get('graph_id', 'unknown')
        
        return {
            'id': graph_id,
            'displayName': props.get('displayName', resource.name),
            'description': props.get('description'),
            'mailEnabled': props.get('mailEnabled', False),
            'mailNickname': props.get('mailNickname'),
            'securityEnabled': props.get('securityEnabled', True),
            'groupTypes': props.get('groupTypes', [])
        }
    
    def _format_directory_object(self, resource: GenericResource) -> Dict:
        """Format as generic directory object"""
        
        if resource.type == 'Microsoft.Graph/User':
            return self._format_graph_user(resource)
        elif resource.type == 'Microsoft.Graph/Group':
            return self._format_graph_group(resource)
        else:
            return {
                'id': resource.tags.get('graph_id', 'unknown'),
                '@odata.type': f"#{resource.type.split('/')[-1].lower()}",
                'displayName': resource.name
            }
    
    def _apply_odata_filter(self, queryset, filter_expr: str):
        """Apply OData $filter expressions (simplified)
        
        Examples:
        - displayName eq 'John Doe'
        - startswith(displayName, 'John')
        - accountEnabled eq true
        """
        
        # Simple equality filter
        import re
        match = re.match(r"(\w+)\s+eq\s+'(.+)'", filter_expr)
        if match:
            field, value = match.groups()
            # Map to MongoDB query
            if field == 'displayName':
                return queryset.filter(name=value)
            else:
                return queryset.filter(**{f'properties__{field}': value})
        
        # startswith function
        match = re.match(r"startswith\((\w+),\s*'(.+)'\)", filter_expr, re.IGNORECASE)
        if match:
            field, prefix = match.groups()
            if field == 'displayName':
                return queryset.filter(name__istartswith=prefix)
        
        return queryset


# FastAPI routes
@router.get("/users")
async def get_users(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    select: Optional[str] = Query(None, alias="$select"),
    filter_expr: Optional[str] = Query(None, alias="$filter"),
    service: GraphService = Depends(lambda: GraphService(StateManager()))
):
    """List users"""
    select_fields = select.split(',') if select else None
    return await service.list_users(top, skip, select_fields, filter_expr)

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    select: Optional[str] = Query(None, alias="$select"),
    service: GraphService = Depends(lambda: GraphService(StateManager()))
):
    """Get user by ID"""
    select_fields = select.split(',') if select else None
    return await service.get_user(user_id, select_fields)

@router.get("/groups")
async def get_groups(
    top: int = Query(100, alias="$top"),
    skip: int = Query(0, alias="$skip"),
    filter_expr: Optional[str] = Query(None, alias="$filter"),
    service: GraphService = Depends(lambda: GraphService(StateManager()))
):
    """List groups"""
    return await service.list_groups(top, skip, filter_expr)

@router.get("/groups/{group_id}/members")
async def get_group_members(
    group_id: str,
    top: int = Query(100, alias="$top"),
    service: GraphService = Depends(lambda: GraphService(StateManager()))
):
    """List group members"""
    return await service.list_group_members(group_id, top)
```

---

### 5. Snapshot Export/Import for Test Fixtures

**Objective:** Enable deterministic test scenarios by exporting discovery snapshots as reusable fixtures.

#### Implementation

```python
# mazure/scenarios/snapshot_manager.py
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from azure_discovery.adt_types import ResourceNode, ResourceRelationship
from ..seeding.discovery_importer import DiscoveryStateSeeder
from ..core.state import StateManager

class SnapshotManager:
    """Manage discovery snapshots as test fixtures"""
    
    async def export_snapshot(
        self,
        nodes: List[ResourceNode],
        relationships: List[ResourceRelationship],
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Export discovery results as JSON fixture
        
        Args:
            nodes: List of ResourceNode objects from discovery
            relationships: List of ResourceRelationship objects
            output_path: Path to write JSON snapshot
            metadata: Optional metadata (tenant info, timestamps, etc.)
        """
        
        snapshot = {
            'metadata': {
                'created_at': datetime.utcnow().isoformat(),
                'mazure_version': '0.2.0',
                'discovery_version': '1.0.0',
                'node_count': len(nodes),
                'relationship_count': len(relationships),
                **(metadata or {})
            },
            'nodes': [n.dict() for n in nodes],
            'relationships': [r.dict() for r in relationships]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"Exported {len(nodes)} nodes and {len(relationships)} relationships to {output_path}")
    
    async def load_snapshot(
        self,
        snapshot_path: Path
    ) -> tuple[List[ResourceNode], List[ResourceRelationship]]:
        """Load snapshot from JSON file
        
        Returns:
            Tuple of (nodes, relationships)
        """
        
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")
        
        with open(snapshot_path) as f:
            data = json.load(f)
        
        # Reconstruct Pydantic models
        nodes = [ResourceNode(**n) for n in data['nodes']]
        relationships = [ResourceRelationship(**r) for r in data['relationships']]
        
        print(f"Loaded {len(nodes)} nodes from snapshot (created: {data['metadata']['created_at']})")
        
        return nodes, relationships
    
    async def seed_from_snapshot(
        self,
        snapshot_path: Path,
        state_manager: StateManager,
        clear_existing: bool = False
    ):
        """Seed mazure state from saved snapshot
        
        Args:
            snapshot_path: Path to JSON snapshot file
            state_manager: StateManager instance
            clear_existing: If True, clear existing state before seeding
        """
        
        if clear_existing:
            await self._clear_state(state_manager)
        
        nodes, relationships = await self.load_snapshot(snapshot_path)
        
        seeder = DiscoveryStateSeeder(state_manager)
        
        # Import nodes
        for node in nodes:
            if not node.id.startswith('graph://'):
                await seeder._import_arm_resource(node)
            else:
                await seeder._import_graph_object(node)
        
        # Import relationships
        for rel in relationships:
            await seeder._import_relationship(rel)
        
        print(f"Seeded {len(nodes)} resources and {len(relationships)} relationships")
    
    async def _clear_state(self, state_manager: StateManager):
        """Clear all existing mock state"""
        from ..core.state import GenericResource
        from ..core.relationships import ResourceRelationship
        
        GenericResource.objects.delete()
        ResourceRelationship.objects.delete()
        print("Cleared existing state")
    
    def list_snapshots(self, fixtures_dir: Path) -> List[Dict[str, Any]]:
        """List available snapshot fixtures
        
        Returns list of snapshot metadata.
        """
        
        snapshots = []
        for snapshot_file in fixtures_dir.glob('**/*.json'):
            try:
                with open(snapshot_file) as f:
                    data = json.load(f)
                    snapshots.append({
                        'path': str(snapshot_file.relative_to(fixtures_dir)),
                        'metadata': data.get('metadata', {})
                    })
            except Exception as e:
                print(f"Warning: Could not read {snapshot_file}: {e}")
        
        return snapshots
```

**CLI Integration:**
```python
# mazure/cli/snapshot.py
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
async def load(
    snapshot_path: Path = typer.Argument(..., help="Path to snapshot JSON file"),
    clear: bool = typer.Option(False, "--clear", help="Clear existing state first")
):
    """Load snapshot into mazure mock state"""
    
    from ..scenarios.snapshot_manager import SnapshotManager
    from ..core.state import StateManager
    
    manager = SnapshotManager()
    await manager.seed_from_snapshot(snapshot_path, StateManager(), clear_existing=clear)
    typer.echo(f"✓ Loaded snapshot from {snapshot_path}")

@app.command()
def list(
    fixtures_dir: Path = typer.Option(Path('fixtures'), "--dir", help="Fixtures directory")
):
    """List available snapshot fixtures"""
    
    from ..scenarios.snapshot_manager import SnapshotManager
    
    manager = SnapshotManager()
    snapshots = manager.list_snapshots(fixtures_dir)
    
    if not snapshots:
        typer.echo("No snapshots found")
        return
    
    typer.echo(f"Found {len(snapshots)} snapshot(s):\n")
    for snap in snapshots:
        meta = snap['metadata']
        typer.echo(f"  {snap['path']}")
        typer.echo(f"    Created: {meta.get('created_at', 'unknown')}")
        typer.echo(f"    Nodes: {meta.get('node_count', 0)}")
        typer.echo(f"    Relationships: {meta.get('relationship_count', 0)}")
        typer.echo()
```

**Usage in Tests:**
```python
# tests/conftest.py
import pytest
from pathlib import Path
from mazure.scenarios.snapshot_manager import SnapshotManager
from mazure.core.state import StateManager

@pytest.fixture(scope='session')
async def mock_azure_environment():
    """Load production-like Azure topology for tests"""
    
    snapshot_path = Path('fixtures/prod-topology.json')
    
    manager = SnapshotManager()
    state = StateManager()
    
    # Clear and load snapshot
    await manager.seed_from_snapshot(snapshot_path, state, clear_existing=True)
    
    yield state
    
    # Cleanup
    from mazure.core.state import GenericResource
    GenericResource.objects.delete()

# tests/test_compute.py
import pytest
from azure.mgmt.compute import ComputeManagementClient
from mazure import mazure

@mazure
@pytest.mark.usefixtures('mock_azure_environment')
def test_list_vms_with_real_topology(mock_credentials):
    """Test VM listing using seeded production topology"""
    
    client = ComputeManagementClient(mock_credentials, 'mock-subscription')
    vms = list(client.virtual_machines.list_all())
    
    # Should reflect actual production VM count from snapshot
    assert len(vms) > 0
    assert all(vm.location in ['eastus', 'westus2'] for vm in vms)
```

---

### 6. Realistic Response Generation

**Objective:** Use discovery data to generate statistically realistic mock responses for resources not in snapshots.

#### Implementation

```python
# mazure/codegen/response_synthesizer.py
from collections import Counter
from typing import Dict, Any, List, Optional
import random
from azure_discovery.adt_types import ResourceNode

class ResponseSynthesizer:
    """Generate realistic responses based on discovery patterns
    
    Analyzes historical discovery data to learn patterns and generate
    statistically realistic mock resources.
    """
    
    def __init__(self, historical_nodes: List[ResourceNode]):
        """Initialize with historical discovery data
        
        Args:
            historical_nodes: List of ResourceNode objects from past discoveries
        """
        self.nodes = historical_nodes
        self._analyze_patterns()
    
    def _analyze_patterns(self):
        """Analyze patterns in discovered resources"""
        
        # Resource type frequency
        self.type_counts = Counter(n.type for n in self.nodes)
        
        # Location distribution per type
        self.location_distribution = {}
        for node in self.nodes:
            if node.type not in self.location_distribution:
                self.location_distribution[node.type] = Counter()
            if node.location:
                self.location_distribution[node.type][node.location] += 1
        
        # Tag patterns
        self.tag_patterns = self._extract_tag_patterns()
        
        # Property patterns per type
        self.property_patterns = self._extract_property_patterns()
        
        print(f"Analyzed {len(self.nodes)} resources across {len(self.type_counts)} types")
    
    def _extract_tag_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Extract common tag keys and value patterns per resource type
        
        Returns:
            Dict mapping resource_type -> tag_key -> list of observed values
        """
        
        patterns = {}
        for node in self.nodes:
            if node.type not in patterns:
                patterns[node.type] = {}
            
            if node.tags:
                for key, value in node.tags.items():
                    if key.startswith('_'):  # Skip internal tags
                        continue
                    if key not in patterns[node.type]:
                        patterns[node.type][key] = []
                    if value and value not in patterns[node.type][key]:
                        patterns[node.type][key].append(value)
        
        return patterns
    
    def _extract_property_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Extract property patterns per resource type
        
        Returns:
            Dict mapping resource_type -> property_key -> pattern info
        """
        
        patterns = {}
        for node in self.nodes:
            if node.type not in patterns:
                patterns[node.type] = {}
            
            if node.properties:
                for key, value in node.properties.items():
                    if key not in patterns[node.type]:
                        patterns[node.type][key] = {
                            'type': type(value).__name__,
                            'values': [],
                            'null_count': 0
                        }
                    
                    if value is None:
                        patterns[node.type][key]['null_count'] += 1
                    else:
                        # Store sample values (up to 10 unique)
                        if len(patterns[node.type][key]['values']) < 10:
                            if value not in patterns[node.type][key]['values']:
                                patterns[node.type][key]['values'].append(value)
        
        return patterns
    
    def synthesize_resource(
        self,
        resource_type: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        override_properties: Optional[Dict[str, Any]] = None,
        override_tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate realistic resource based on observed patterns
        
        Args:
            resource_type: Azure resource type (e.g., 'Microsoft.Compute/virtualMachines')
            name: Resource name (auto-generated if not provided)
            location: Azure region (selected based on distribution if not provided)
            override_properties: Explicit property values to use
            override_tags: Explicit tag values to use
        
        Returns:
            Dict representing a realistic ARM resource
        """
        
        # Find similar resources as templates
        similar = [n for n in self.nodes if n.type == resource_type]
        
        if not similar:
            raise ValueError(f"No examples found for {resource_type}. Consider seeding more data.")
        
        # Pick a template resource
        template = random.choice(similar)
        
        # Generate properties
        properties = {}
        if resource_type in self.property_patterns:
            for prop_key, pattern_info in self.property_patterns[resource_type].items():
                if pattern_info['values']:
                    # Use observed value
                    properties[prop_key] = random.choice(pattern_info['values'])
                elif pattern_info['type'] == 'str':
                    properties[prop_key] = f"mock-{prop_key}"
                elif pattern_info['type'] == 'int':
                    properties[prop_key] = random.randint(1, 100)
                elif pattern_info['type'] == 'bool':
                    properties[prop_key] = random.choice([True, False])
        
        # Apply overrides
        if override_properties:
            properties.update(override_properties)
        
        # Pick realistic location
        if not location:
            if resource_type in self.location_distribution and self.location_distribution[resource_type]:
                location = random.choices(
                    list(self.location_distribution[resource_type].keys()),
                    weights=list(self.location_distribution[resource_type].values()),
                    k=1
                )[0]
            else:
                location = 'eastus'  # Default fallback
        
        # Generate realistic tags
        tags = {}
        if resource_type in self.tag_patterns:
            for tag_key, values in self.tag_patterns[resource_type].items():
                if random.random() < 0.7:  # 70% chance to include each tag
                    tags[tag_key] = random.choice(values)
        
        # Apply tag overrides
        if override_tags:
            tags.update(override_tags)
        
        # Generate name if not provided
        if not name:
            prefix = template.name.split('-')[0] if '-' in template.name else template.name
            name = f"{prefix}-{random.randint(1000, 9999)}"
        
        return {
            'type': resource_type,
            'name': name,
            'location': location,
            'properties': properties,
            'tags': tags
        }
    
    def synthesize_batch(
        self,
        resource_type: str,
        count: int,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate multiple realistic resources
        
        Args:
            resource_type: Azure resource type
            count: Number of resources to generate
            **kwargs: Passed to synthesize_resource()
        
        Returns:
            List of resource dictionaries
        """
        
        return [
            self.synthesize_resource(resource_type, **kwargs)
            for _ in range(count)
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns
        
        Returns:
            Dict with pattern statistics
        """
        
        return {
            'total_resources': len(self.nodes),
            'resource_types': dict(self.type_counts.most_common()),
            'tag_keys_per_type': {
                rt: list(tags.keys())
                for rt, tags in self.tag_patterns.items()
            },
            'locations': set(
                loc
                for dist in self.location_distribution.values()
                for loc in dist.keys()
            )
        }
```

**Usage Example:**
```python
# In service implementations
from mazure.codegen.response_synthesizer import ResponseSynthesizer

# Load historical discovery data
from mazure.scenarios.snapshot_manager import SnapshotManager

manager = SnapshotManager()
nodes, _ = await manager.load_snapshot('fixtures/prod-topology.json')

# Initialize synthesizer
synth = ResponseSynthesizer(nodes)

# Generate realistic VM when not found in state
if not vm:
    realistic_vm = synth.synthesize_resource(
        resource_type='Microsoft.Compute/virtualMachines',
        name='test-vm-001',
        override_properties={'vmSize': 'Standard_D2s_v3'}
    )
```

---

### 7. AutoRest Integration Enhancement

**Objective:** Extend the existing AutoRest plan to use discovery data for validation and schema generation.

#### Implementation

```python
# mazure/sync/discovery_validator.py
from pathlib import Path
from typing import Dict, Any, List, Set
import os
from azure_discovery import AzureDiscoveryRequest, run_discovery

class DiscoveryBasedValidator:
    """Validate generated code against live Azure structure
    
    Ensures generated service implementations accurately reflect
    real Azure API behavior by comparing against discovery samples.
    """
    
    async def validate_service_implementation(
        self,
        resource_type: str,
        implementation_path: Path,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compare generated service against discovery samples
        
        Args:
            resource_type: Azure resource type to validate
            implementation_path: Path to generated service code
            tenant_id: Optional tenant ID for live discovery (uses env var if not provided)
        
        Returns:
            Validation report with coverage metrics
        """
        
        # Run discovery to get real samples
        tenant_id = tenant_id or os.getenv('AZURE_TENANT_ID')
        if not tenant_id:
            return {
                'status': 'skipped',
                'reason': 'No tenant ID provided for live validation'
            }
        
        try:
            request = AzureDiscoveryRequest(
                tenant_id=tenant_id,
                include_type=[resource_type],
                entra_max_objects=10  # Just need samples
            )
            response = await run_discovery(request)
        except Exception as e:
            return {
                'status': 'discovery_failed',
                'error': str(e)
            }
        
        samples = [n for n in response.nodes if n.type == resource_type]
        
        if not samples:
            return {
                'status': 'no_samples',
                'coverage': 0,
                'message': f'No live {resource_type} resources found for validation'
            }
        
        # Analyze implementation
        implemented_properties = self._extract_implemented_properties(implementation_path)
        implemented_operations = self._extract_implemented_operations(implementation_path)
        
        # Analyze samples
        all_properties = set()
        for sample in samples:
            if sample.properties:
                all_properties.update(sample.properties.keys())
        
        # Calculate coverage
        if all_properties:
            property_coverage = len(implemented_properties & all_properties) / len(all_properties)
        else:
            property_coverage = 1.0  # No properties to implement
        
        missing_properties = list(all_properties - implemented_properties)
        extra_properties = list(implemented_properties - all_properties)
        
        return {
            'status': 'validated',
            'resource_type': resource_type,
            'sample_count': len(samples),
            'property_coverage': round(property_coverage * 100, 2),
            'missing_properties': missing_properties[:10],  # Top 10
            'extra_properties': extra_properties[:10],
            'implemented_operations': list(implemented_operations),
            'recommendations': self._generate_recommendations(
                missing_properties,
                extra_properties,
                samples
            )
        }
    
    def _extract_implemented_properties(self, implementation_path: Path) -> Set[str]:
        """Parse service implementation to find handled properties
        
        Looks for property keys in schemas and service code.
        """
        
        if not implementation_path.exists():
            return set()
        
        properties = set()
        
        with open(implementation_path) as f:
            content = f.read()
            
            # Look for property access patterns: properties.get('key') or ['key']
            import re
            
            # Pattern: properties.get('propertyName')
            get_matches = re.findall(r"properties\.get\(['\"]([\w_]+)['\"]\)", content)
            properties.update(get_matches)
            
            # Pattern: properties['propertyName']
            bracket_matches = re.findall(r"properties\[['\"]([\w_]+)['\"]\]", content)
            properties.update(bracket_matches)
            
            # Pattern: Pydantic field definitions
            field_matches = re.findall(r"^\s+(\w+):\s+(?:Optional\[)?\w+(?:\])?\s*(?:=|,)", content, re.MULTILINE)
            properties.update(field_matches)
        
        return properties
    
    def _extract_implemented_operations(self, implementation_path: Path) -> Set[str]:
        """Find implemented CRUD operations"""
        
        if not implementation_path.exists():
            return set()
        
        operations = set()
        
        with open(implementation_path) as f:
            content = f.read()
            
            # Look for standard operations
            if 'async def create' in content or 'def create' in content:
                operations.add('CREATE')
            if 'async def get' in content or 'def get' in content:
                operations.add('GET')
            if 'async def update' in content or 'def update' in content:
                operations.add('UPDATE')
            if 'async def delete' in content or 'def delete' in content:
                operations.add('DELETE')
            if 'async def list' in content or 'def list' in content:
                operations.add('LIST')
        
        return operations
    
    def _generate_recommendations(
        self,
        missing: List[str],
        extra: List[str],
        samples: List
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if missing:
            recommendations.append(
                f"Add support for {len(missing)} missing properties: {', '.join(missing[:5])}"
            )
        
        if extra:
            recommendations.append(
                f"Review {len(extra)} extra properties not seen in samples: {', '.join(extra[:5])}"
            )
        
        if not missing and not extra:
            recommendations.append("Implementation matches discovered schema! ✓")
        
        return recommendations
```

**CLI Integration:**
```python
# mazure/cli/validate.py
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
async def service(
    resource_type: str = typer.Argument(..., help="Resource type to validate"),
    implementation: Path = typer.Option(None, "--impl", help="Path to service implementation"),
    tenant_id: str = typer.Option(None, "--tenant-id", help="Azure tenant ID for live validation")
):
    """Validate service implementation against live Azure"""
    
    from ..sync.discovery_validator import DiscoveryBasedValidator
    
    if not implementation:
        # Auto-detect implementation path
        provider = resource_type.split('/')[0].replace('.', '_').lower()
        impl_name = resource_type.split('/')[1].lower() + '.py'
        implementation = Path(f'mazure/services/{provider}/{impl_name}')
    
    validator = DiscoveryBasedValidator()
    report = await validator.validate_service_implementation(
        resource_type,
        implementation,
        tenant_id
    )
    
    typer.echo(f"\n📊 Validation Report: {resource_type}\n")
    typer.echo(f"Status: {report['status']}")
    
    if report['status'] == 'validated':
        typer.echo(f"Sample Count: {report['sample_count']}")
        typer.echo(f"Property Coverage: {report['property_coverage']}%")
        typer.echo(f"Operations: {', '.join(report['implemented_operations'])}")
        
        if report['missing_properties']:
            typer.echo(f"\n⚠ Missing Properties:")
            for prop in report['missing_properties']:
                typer.echo(f"  - {prop}")
        
        typer.echo(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            typer.echo(f"  • {rec}")
```

---

### 8. Dynamic Mock Behavior from Relationships

**Objective:** Use relationship data to implement cascading operations and dependency validation.

#### Implementation

```python
# mazure/core/relationship_engine.py
from typing import List, Dict, Any, Set
from .state import StateManager, GenericResource

class ResourceRelationship(db.Document):
    """MongoDB model for resource relationships"""
    
    source_id = db.StringField(required=True)
    target_id = db.StringField(required=True)
    relation_type = db.StringField(required=True)  # contains, depends_on, has_member, etc.
    weight = db.FloatField(default=1.0)
    metadata = db.DictField()
    
    meta = {
        'collection': 'relationships',
        'indexes': [
            ('source_id', 'relation_type'),
            ('target_id', 'relation_type')
        ]
    }

class RelationshipEngine:
    """Handle cascading operations based on resource relationships
    
    Uses relationship data from discovery to implement:
    - Cascading deletes
    - Dependency validation
    - Impact analysis
    - Resource group operations
    """
    
    def __init__(self, state: StateManager):
        self.state = state
    
    async def delete_with_dependents(
        self,
        resource_id: str,
        cascade: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Delete resource and optionally cascade to dependents
        
        Args:
            resource_id: ARM resource ID
            cascade: If True, delete dependent resources
            dry_run: If True, return what would be deleted without deleting
        
        Returns:
            Dict with deleted resource IDs and dependency info
        """
        
        # Find all relationships where this resource is the source
        outbound_rels = ResourceRelationship.objects(source_id=resource_id)
        
        # Find all relationships where this resource is the target (dependents)
        inbound_rels = ResourceRelationship.objects(target_id=resource_id)
        
        deleted_ids = []
        blocked_by = []
        warnings = []
        
        # Check for blocking dependencies
        for rel in inbound_rels:
            if rel.relation_type in ['depends_on', 'required_by']:
                if not cascade:
                    blocked_by.append({
                        'resource_id': rel.source_id,
                        'relation_type': rel.relation_type
                    })
        
        if blocked_by and not cascade:
            raise ValueError(
                f"Cannot delete {resource_id}: has dependent resources. "
                f"Use cascade=True to delete dependents, or remove dependencies first."
            )
        
        # Build deletion plan
        to_delete = await self._build_deletion_tree(
            resource_id,
            cascade,
            visited=set()
        )
        
        if dry_run:
            return {
                'dry_run': True,
                'would_delete': to_delete,
                'count': len(to_delete),
                'warnings': warnings
            }
        
        # Execute deletions in reverse dependency order
        for rid in reversed(to_delete):
            # Delete resource
            parts = rid.split('/')
            if 'subscriptions' in parts and 'resourceGroups' in parts:
                sub_idx = parts.index('subscriptions') + 1
                rg_idx = parts.index('resourceGroups') + 1
                
                subscription_id = parts[sub_idx]
                resource_group = parts[rg_idx]
                
                # Extract resource type and name
                if 'providers' in parts:
                    prov_idx = parts.index('providers')
                    resource_type = f"{parts[prov_idx + 1]}/{parts[prov_idx + 2]}"
                    name = parts[-1]
                    
                    success = await self.state.delete_resource(
                        subscription_id,
                        resource_group,
                        resource_type,
                        name
                    )
                    
                    if success:
                        deleted_ids.append(rid)
            
            # Delete relationships
            ResourceRelationship.objects(Q(source_id=rid) | Q(target_id=rid)).delete()
        
        return {
            'deleted': deleted_ids,
            'count': len(deleted_ids),
            'cascade': cascade,
            'warnings': warnings
        }
    
    async def _build_deletion_tree(
        self,
        resource_id: str,
        cascade: bool,
        visited: Set[str]
    ) -> List[str]:
        """Build ordered list of resources to delete
        
        Uses depth-first traversal to build deletion order.
        """
        
        if resource_id in visited:
            return []
        
        visited.add(resource_id)
        to_delete = []
        
        if cascade:
            # Find resources contained by or dependent on this one
            child_rels = ResourceRelationship.objects(
                source_id=resource_id,
                relation_type__in=['contains', 'parent_of']
            )
            
            dependent_rels = ResourceRelationship.objects(
                target_id=resource_id,
                relation_type__in=['depends_on', 'child_of']
            )
            
            # Recursively add children
            for rel in child_rels:
                child_tree = await self._build_deletion_tree(
                    rel.target_id,
                    cascade=True,
                    visited=visited
                )
                to_delete.extend(child_tree)
            
            # Recursively add dependents
            for rel in dependent_rels:
                dep_tree = await self._build_deletion_tree(
                    rel.source_id,
                    cascade=True,
                    visited=visited
                )
                to_delete.extend(dep_tree)
        
        # Add this resource last (delete children first)
        to_delete.append(resource_id)
        
        return to_delete
    
    async def validate_create(
        self,
        resource_type: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate resource creation against dependencies
        
        Checks if required resources exist (e.g., subnet for VM NIC).
        """
        
        errors = []
        warnings = []
        
        # Check resource-type-specific dependencies
        if resource_type == 'Microsoft.Compute/virtualMachines':
            # Require network interface
            nic_refs = properties.get('networkProfile', {}).get('networkInterfaces', [])
            for nic_ref in nic_refs:
                nic_id = nic_ref.get('id')
                if nic_id:
                    nic_exists = await self._resource_exists(nic_id)
                    if not nic_exists:
                        errors.append(f"Referenced network interface not found: {nic_id}")
        
        elif resource_type == 'Microsoft.Network/networkInterfaces':
            # Require subnet
            subnet_ref = properties.get('ipConfigurations', [{}])[0].get('subnet', {}).get('id')
            if subnet_ref:
                subnet_exists = await self._resource_exists(subnet_ref)
                if not subnet_exists:
                    errors.append(f"Referenced subnet not found: {subnet_ref}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def _resource_exists(self, resource_id: str) -> bool:
        """Check if resource exists in mock state"""
        resource = GenericResource.objects(resource_id=resource_id).first()
        return resource is not None
    
    async def get_resource_dependencies(
        self,
        resource_id: str,
        depth: int = 1
    ) -> Dict[str, Any]:
        """Get dependency tree for a resource
        
        Args:
            resource_id: ARM resource ID
            depth: How many levels deep to traverse (0 = infinite)
        
        Returns:
            Dependency tree with inbound and outbound relationships
        """
        
        # Get outbound relationships (resources this depends on)
        outbound = ResourceRelationship.objects(source_id=resource_id)
        
        # Get inbound relationships (resources that depend on this)
        inbound = ResourceRelationship.objects(target_id=resource_id)
        
        tree = {
            'resource_id': resource_id,
            'depends_on': [],
            'depended_by': []
        }
        
        for rel in outbound:
            dep = {
                'resource_id': rel.target_id,
                'relation_type': rel.relation_type,
                'weight': rel.weight
            }
            
            # Recursive traversal
            if depth != 1:
                next_depth = depth - 1 if depth > 0 else 0
                dep['dependencies'] = await self.get_resource_dependencies(
                    rel.target_id,
                    depth=next_depth
                )
            
            tree['depends_on'].append(dep)
        
        for rel in inbound:
            dep = {
                'resource_id': rel.source_id,
                'relation_type': rel.relation_type,
                'weight': rel.weight
            }
            
            tree['depended_by'].append(dep)
        
        return tree
```

**Usage in Service Implementations:**
```python
# mazure/services/compute/virtual_machines.py
from ...core.relationship_engine import RelationshipEngine

class VirtualMachineService:
    def __init__(self, state: StateManager):
        self.state = state
        self.relationships = RelationshipEngine(state)
    
    async def delete(
        self,
        subscription_id: str,
        resource_group: str,
        vm_name: str,
        force: bool = False
    ) -> bool:
        """Delete virtual machine with dependency handling"""
        
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
        
        # Check dependencies
        result = await self.relationships.delete_with_dependents(
            resource_id,
            cascade=force,
            dry_run=not force
        )
        
        if result.get('dry_run'):
            # Return what would be deleted
            return {
                'status': 'requires_confirmation',
                'would_delete': result['would_delete'],
                'message': 'Use force=True to delete VM and dependencies'
            }
        
        return result['count'] > 0
```

---

## Implementation Roadmap

### Phase 1: Foundation (2-3 weeks)
**Goal:** Basic discovery-to-mock pipeline

**Tasks:**
1. Implement `DiscoveryStateSeeder` with ARM resource import
   - Parse resource IDs correctly
   - Handle all resource types generically
   - Preserve discovery metadata

2. Add CLI command `mazure seed from-azure`
   - Support tenant ID and subscription filters
   - Add progress indicators
   - Handle authentication gracefully

3. Extend `StateManager` to support relationship storage
   - Create `ResourceRelationship` MongoDB model
   - Add indexes for efficient queries
   - Implement relationship CRUD operations

4. Create snapshot export/import functionality
   - JSON serialization of discovery results
   - Validation of snapshot schema
   - CLI commands for snapshot management

**Deliverables:**
- Working `mazure seed` command
- Snapshot fixtures in `fixtures/` directory
- Documentation for seeding workflow
- Unit tests for state seeding

**Success Criteria:**
- Can seed 100+ resources from live Azure
- Snapshot loading works consistently
- MongoDB state matches discovery output

---

### Phase 2: Query Engine (3-4 weeks)
**Goal:** Resource Graph and Graph API support

**Tasks:**
1. Implement basic Resource Graph query parser
   - Support WHERE, PROJECT, TAKE operators
   - Handle type and location filters
   - Parse KQL syntax (simplified subset)

2. Add Graph API mock endpoints
   - `/v1.0/users` (list and get)
   - `/v1.0/groups` (list and get members)
   - `/v1.0/applications`
   - `/v1.0/servicePrincipals`

3. Integrate relationship-based queries
   - Group membership expansion
   - Application ownership
   - Service principal correlation

4. Add pagination and filtering support
   - OData `$top`, `$skip`, `$filter`
   - Next link generation
   - Filter expression parsing

**Deliverables:**
- Resource Graph `/providers/Microsoft.ResourceGraph/resources` endpoint
- Graph API v1.0 endpoints mounted at `/v1.0`
- Documentation for query syntax support
- Integration tests with seeded state

**Success Criteria:**
- Basic Resource Graph queries work
- Graph API returns realistic responses
- Pagination functions correctly
- Relationships are queryable

---

### Phase 3: Intelligence Layer (2-3 weeks)
**Goal:** Realistic data generation and validation

**Tasks:**
1. Implement `ResponseSynthesizer`
   - Analyze property patterns from samples
   - Generate statistically realistic resources
   - Support tag and location distributions

2. Add schema inference from discovery samples
   - Generate Pydantic models dynamically
   - Detect field types and nullability
   - Export schemas to modules

3. Create validation framework against live Azure
   - Compare implementations to discovery
   - Calculate property coverage
   - Generate actionable recommendations

4. Build test fixture library from snapshots
   - pytest fixtures for common scenarios
   - Parameterized tests using snapshots
   - Documentation for test authoring

**Deliverables:**
- `ResponseSynthesizer` class with pattern learning
- `SchemaGenerator` for dynamic Pydantic models
- `DiscoveryBasedValidator` for implementation checking
- Test fixtures and examples

**Success Criteria:**
- Generated resources look realistic
- Schemas match live Azure APIs
- Validation reports actionable gaps
- Tests use snapshot fixtures

---

### Phase 4: Production Hardening (2-3 weeks)
**Goal:** Enterprise-ready features

**Tasks:**
1. Add comprehensive error scenarios
   - Simulate Azure throttling (429 errors)
   - Resource not found (404)
   - Conflict errors (409)
   - Validation failures (400)

2. Implement API version compatibility matrix
   - Track supported API versions per service
   - Validate version in requests
   - Return appropriate errors for unsupported versions

3. Add performance benchmarks
   - Query performance metrics
   - State seeding speed
   - Memory usage profiling
   - Load testing scenarios

4. Create documentation and examples
   - Getting started guide
   - API reference
   - Integration patterns
   - Troubleshooting guide
   - Migration from manual mocks

**Deliverables:**
- Error scenario framework
- API version compatibility checker
- Performance benchmark suite
- Comprehensive documentation
- Example projects

**Success Criteria:**
- Realistic error responses
- Version validation working
- Performance baselines established
- Documentation complete

---

## Key Benefits

### 1. Zero Manual Maintenance
Mazure stays synchronized with Azure API changes automatically via AzureDiscovery's continuous enumeration. No more manually updating mock responses when Azure adds new properties or services.

### 2. Realistic Test Data
Mock responses reflect actual Azure resource structures from your environment, not hand-crafted examples that may be outdated or incomplete.

### 3. Topology-Aware Testing
Relationship modeling enables testing of cascading operations, dependency validation, and impact analysis—critical for infrastructure-as-code scenarios.

### 4. Multi-Cloud Support
AzureDiscovery's cloud-aware architecture (Public, Government, China, Germany) translates directly to mazure, enabling testing across sovereign clouds without code changes.

### 5. Compliance Testing
Seeded Entra data enables RBAC, conditional access, and identity-driven test scenarios. Test security policies without touching production identity systems.

### 6. Deterministic Tests
Snapshot fixtures provide reproducible test environments. Commit snapshots to version control for consistent CI/CD execution.

### 7. Reduced Test Infrastructure Costs
Eliminate expensive Azure test subscriptions. Run entire integration test suites locally or in CI without live Azure resources.

### 8. Faster Test Execution
Local mocks respond in milliseconds vs. seconds for live Azure API calls. Dramatically faster test suites enable rapid development cycles.

---

## Example Workflows

### Workflow 1: Seeding from Production
```bash
# 1. Discover production environment
mazure seed from-azure <tenant-id> \
  --subscription <prod-sub-id> \
  --include-entra \
  --output fixtures/prod-snapshot.json

# 2. Load snapshot in tests
mazure snapshot load fixtures/prod-snapshot.json --clear

# 3. Run test suite against production-like state
pytest tests/integration/
```

### Workflow 2: Validating Generated Code
```bash
# 1. Generate service from AutoRest
mazure-cli generate Microsoft.Compute virtualMachines 2024-03-01

# 2. Validate against live Azure
mazure validate service Microsoft.Compute/virtualMachines \
  --tenant-id <tenant-id> \
  --impl mazure/services/compute/virtual_machines.py

# 3. Review coverage report and fix gaps
```

### Workflow 3: Testing Cascading Deletes
```python
import pytest
from mazure import mazure
from mazure.scenarios.snapshot_manager import SnapshotManager

@pytest.fixture
async def azure_env_with_dependencies():
    """Load snapshot with VMs, NICs, and VNets"""
    manager = SnapshotManager()
    await manager.seed_from_snapshot('fixtures/networking-scenario.json')

@mazure
@pytest.mark.usefixtures('azure_env_with_dependencies')
async def test_delete_vm_cascade():
    """Test that deleting a VM with force=True deletes dependent NICs"""
    
    from mazure.services.compute import VirtualMachineService
    
    service = VirtualMachineService(StateManager())
    
    # Delete VM with cascade
    result = await service.delete(
        subscription_id='mock-sub',
        resource_group='test-rg',
        vm_name='test-vm',
        force=True
    )
    
    # Verify VM and NICs deleted
    assert result['count'] == 2  # VM + NIC
    assert 'virtualMachines/test-vm' in result['deleted'][0]
    assert 'networkInterfaces' in result['deleted'][1]
```

### Workflow 4: Generating Realistic Test Data
```python
from mazure.codegen.response_synthesizer import ResponseSynthesizer
from mazure.scenarios.snapshot_manager import SnapshotManager

# Load historical patterns
manager = SnapshotManager()
nodes, _ = await manager.load_snapshot('fixtures/prod-snapshot.json')

# Initialize synthesizer
synth = ResponseSynthesizer(nodes)

# Generate 10 realistic VMs
vms = synth.synthesize_batch(
    resource_type='Microsoft.Compute/virtualMachines',
    count=10,
    override_tags={'environment': 'test'}
)

for vm in vms:
    print(f"Generated VM: {vm['name']} in {vm['location']}")
    print(f"  Properties: {vm['properties'].keys()}")
    print(f"  Tags: {vm['tags']}")
```

---

## Technical Considerations

### MongoDB Schema Evolution
As discovery data includes dynamic properties, MongoDB's flexible schema is ideal. Consider:
- Adding indexes on frequently queried fields (type, subscription_id, resource_group)
- Using TTL indexes for ephemeral test state
- Implementing schema migrations if needed

### Performance at Scale
For large environments (1000+ resources):
- Implement lazy loading of relationships
- Add query result caching
- Consider Redis for high-frequency queries
- Batch relationship imports

### Authentication Handling
Discovery requires Azure credentials:
- Support Azure CLI authentication (DefaultAzureCredential)
- Document service principal setup
- Add credential validation before seeding
- Cache tokens during batch operations

### Multi-Tenancy
To support multiple tenant snapshots:
- Add tenant_id field to all resources
- Isolate state by tenant in tests
- Support tenant switching in CLI
- Document multi-tenant test patterns

### CI/CD Integration
For automated testing:
- Commit snapshots to version control
- Update snapshots weekly via scheduled job
- Validate snapshot integrity in CI
- Generate coverage reports

---

## Migration Guide

For existing mazure users, migration is incremental:

### Step 1: Install AzureDiscovery
```bash
pip install azure-discovery
```

### Step 2: Seed Initial State
```bash
mazure seed from-azure <tenant-id> --output fixtures/baseline.json
```

### Step 3: Update Tests
```python
# Before:
@mazure
def test_vm_creation():
    client = ComputeManagementClient(...)
    vm = client.virtual_machines.create_or_update(...)

# After:
@pytest.fixture
def seeded_env():
    manager = SnapshotManager()
    manager.seed_from_snapshot('fixtures/baseline.json')

@mazure
@pytest.mark.usefixtures('seeded_env')
def test_vm_creation():
    # Now operates on realistic pre-seeded state
    client = ComputeManagementClient(...)
    vm = client.virtual_machines.get('test-rg', 'existing-vm')
    assert vm is not None
```

### Step 4: Validate Coverage
```bash
mazure validate service Microsoft.Compute/virtualMachines
```

### Step 5: Iterate
- Update snapshots regularly
- Add more test scenarios
- Expand service coverage

---

## Future Enhancements

### Intelligent Mock Evolution
Use ML to predict Azure API changes based on historical discovery patterns.

### Multi-Region Support
Automatically handle regional differences in Azure APIs.

### Diff-Based Updates
Only update changed resources when refreshing snapshots.

### Visual Topology Viewer
Integrate AzureDiscovery's PyVis graphs into mazure web UI for debugging.

### Chaos Engineering
Inject realistic failures based on observed Azure behavior patterns.

### Performance Replay
Replay actual Azure API latency distributions in mocks.

---

## Conclusion

Integrating AzureDiscovery into mazure transforms it from a manually-maintained mock framework into an intelligent, self-updating testing suite. By leveraging real Azure topology and relationship data, tests become more realistic, maintainable, and resilient to API changes.

The phased approach allows incremental adoption while delivering value at each stage. Start with basic state seeding, then expand to query engines, validation, and advanced features as needed.

This architecture positions mazure as the definitive Azure mocking solution—one that reflects reality, not assumptions.

---

## References

- [AzureDiscovery Repository](https://github.com/maravedi/AzureDiscovery)
- [Mazure Repository](https://github.com/maravedi/mazure)
- [Azure REST API Specifications](https://github.com/Azure/azure-rest-api-specs)
- [Moto (AWS Mocking Library)](https://github.com/spulec/moto)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Azure Resource Graph Documentation](https://docs.microsoft.com/azure/governance/resource-graph/)
- [Microsoft Graph API Documentation](https://docs.microsoft.com/graph/)

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Author:** Technical Architecture Team  
**Status:** Proposal / Implementation Plan
