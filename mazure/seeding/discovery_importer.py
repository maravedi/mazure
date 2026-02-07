"""Import AzureDiscovery enumeration results into mazure state."""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

try:
    from azure_discovery import AzureDiscoveryRequest, run_discovery
    from azure_discovery.adt_types import ResourceNode, ResourceRelationship as DiscoveryRelationship
    AZURE_DISCOVERY_AVAILABLE = True
except ImportError:
    AZURE_DISCOVERY_AVAILABLE = False
    ResourceNode = Any
    DiscoveryRelationship = Any

from ..core.state import StateManager, GenericResource
from ..core.relationships import ResourceRelationship


class DiscoveryStateSeeder:
    """Import AzureDiscovery enumeration results into mazure state.
    
    Transforms discovered Azure resources and relationships into mazure's
    MongoDB-backed mock state, enabling realistic test scenarios based on
    actual production topology.
    """
    
    def __init__(self, state_manager: StateManager):
        """Initialize seeder.
        
        Args:
            state_manager: StateManager instance for accessing mock state
        """
        if not AZURE_DISCOVERY_AVAILABLE:
            raise ImportError(
                "azure-discovery package not installed. "
                "Install with: pip install azure-discovery"
            )
        
        self.state = state_manager
    
    async def seed_from_discovery(
        self,
        discovery_request: 'AzureDiscoveryRequest'
    ) -> Dict[str, int]:
        """Execute discovery and populate mock state with real topology.
        
        Args:
            discovery_request: AzureDiscoveryRequest with tenant, subscriptions, etc.
        
        Returns:
            Dict with statistics: arm_resources, entra_objects, relationships
        """
        print(f"\nStarting discovery for tenant: {discovery_request.tenant_id}")
        print(f"Subscriptions: {', '.join(discovery_request.subscriptions) if discovery_request.subscriptions else 'All'}")
        
        # Run discovery against live Azure
        response = await run_discovery(discovery_request)
        
        stats = {
            'arm_resources': 0,
            'entra_objects': 0,
            'relationships': 0,
            'errors': 0
        }
        
        # Import ARM resources and Entra objects
        print(f"\nImporting {len(response.nodes)} resources...")
        for i, node in enumerate(response.nodes, 1):
            try:
                if not node.id.startswith('graph://'):
                    # ARM resource
                    await self._import_arm_resource(node)
                    stats['arm_resources'] += 1
                else:
                    # Entra/Graph resource
                    await self._import_graph_object(node)
                    stats['entra_objects'] += 1
                
                if i % 50 == 0:
                    print(f"  Imported {i}/{len(response.nodes)} resources...")
            
            except Exception as e:
                print(f"  Error importing {node.id}: {e}")
                stats['errors'] += 1
        
        # Import relationships for dependency modeling
        print(f"\nImporting {len(response.relationships)} relationships...")
        for i, rel in enumerate(response.relationships, 1):
            try:
                await self._import_relationship(rel)
                stats['relationships'] += 1
                
                if i % 100 == 0:
                    print(f"  Imported {i}/{len(response.relationships)} relationships...")
            
            except Exception as e:
                print(f"  Error importing relationship: {e}")
                stats['errors'] += 1
        
        print(f"\n✓ Discovery import complete!")
        print(f"  ARM Resources: {stats['arm_resources']}")
        print(f"  Entra Objects: {stats['entra_objects']}")
        print(f"  Relationships: {stats['relationships']}")
        if stats['errors']:
            print(f"  Errors: {stats['errors']}")
        
        return stats
    
    async def _import_arm_resource(self, node: ResourceNode) -> GenericResource:
        """Convert ResourceNode to GenericResource.
        
        Args:
            node: ResourceNode from AzureDiscovery
        
        Returns:
            Created GenericResource
        """
        # Parse Azure resource ID
        # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{type}/{name}
        parts = node.id.split('/')
        
        try:
            # Extract components from resource ID
            if 'providers' in parts:
                provider_idx = parts.index('providers')
                resource_type = f"{parts[provider_idx + 1]}/{parts[provider_idx + 2]}"
                resource_name = parts[-1]
            else:
                # Fallback for non-standard IDs
                resource_type = node.type
                resource_name = node.name
            
            if 'subscriptions' in parts:
                sub_idx = parts.index('subscriptions') + 1
                subscription_id = parts[sub_idx]
            else:
                subscription_id = node.subscription_id or 'unknown'
            
            if 'resourceGroups' in parts:
                rg_idx = parts.index('resourceGroups') + 1
                resource_group = parts[rg_idx]
            else:
                resource_group = node.resource_group or 'default-rg'
        
        except (IndexError, ValueError) as e:
            # Fallback parsing for edge cases
            print(f"    Warning: Could not parse resource ID {node.id}, using fallback: {e}")
            resource_type = node.type
            resource_name = node.name
            resource_group = node.resource_group or 'default-rg'
            subscription_id = node.subscription_id or 'unknown'
        
        # Create or update resource
        return await self.state.create_resource(
            resource_type=resource_type,
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=resource_name,
            properties=node.properties or {},
            location=node.location or 'global',
            tags=node.tags or {},
            resource_id=node.id,
            # Preserve discovery metadata
            _discovery_metadata={
                'discovered_at': datetime.utcnow().isoformat(),
                'tenant_id': node.tags.get('_tenant_id') if node.tags else None,
                'kind': node.kind if hasattr(node, 'kind') else None
            }
        )
    
    async def _import_graph_object(self, node: ResourceNode) -> GenericResource:
        """Import Entra ID Graph objects as special resource types.
        
        Args:
            node: ResourceNode representing a Graph object
        
        Returns:
            Created GenericResource
        """
        # Store Graph objects as pseudo-resources with special resource group
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
    
    async def _import_relationship(self, rel: DiscoveryRelationship):
        """Store relationship edge for graph queries.
        
        Args:
            rel: ResourceRelationship from AzureDiscovery
        
        Returns:
            Created ResourceRelationship
        """
        return await ResourceRelationship.create_relationship(
            source_id=rel.source_id,
            target_id=rel.target_id,
            relation_type=rel.relation_type,
            weight=rel.weight if hasattr(rel, 'weight') else 1.0
        )
    
    async def export_snapshot(
        self,
        output_path: str,
        nodes: List[ResourceNode],
        relationships: List[DiscoveryRelationship],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Export discovery results as JSON snapshot.
        
        Args:
            output_path: Path to write JSON file
            nodes: List of ResourceNode objects
            relationships: List of ResourceRelationship objects
            metadata: Optional metadata dict
        """
        from pathlib import Path
        import json
        
        snapshot = {
            'metadata': {
                'created_at': datetime.utcnow().isoformat(),
                'mazure_version': '0.2.0',
                'node_count': len(nodes),
                'relationship_count': len(relationships),
                **(metadata or {})
            },
            'nodes': [n.dict() for n in nodes],
            'relationships': [r.dict() for r in relationships]
        }
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"\n✓ Snapshot exported to {output_path}")
        print(f"  Nodes: {len(nodes)}")
        print(f"  Relationships: {len(relationships)}")
