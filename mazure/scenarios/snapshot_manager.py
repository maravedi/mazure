"""Manage discovery snapshots as test fixtures."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    from azure_discovery.adt_types import ResourceNode, ResourceRelationship as DiscoveryRelationship
    AZURE_DISCOVERY_AVAILABLE = True
except ImportError:
    AZURE_DISCOVERY_AVAILABLE = False
    ResourceNode = Any
    DiscoveryRelationship = Any

from ..core.state import StateManager, GenericResource
from ..core.relationships import ResourceRelationship
from ..seeding.discovery_importer import DiscoveryStateSeeder


class SnapshotManager:
    """Manage discovery snapshots as test fixtures.
    
    Provides functionality to:
    - Export discovery results as JSON snapshots
    - Load snapshots into mazure state
    - List available snapshot fixtures
    - Manage snapshot metadata
    """
    
    async def export_snapshot(
        self,
        nodes: List[ResourceNode],
        relationships: List[DiscoveryRelationship],
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Export discovery results as JSON fixture.
        
        Args:
            nodes: List of ResourceNode objects from discovery
            relationships: List of ResourceRelationship objects
            output_path: Path to write JSON snapshot
            metadata: Optional metadata (tenant info, timestamps, etc.)
        """
        if not AZURE_DISCOVERY_AVAILABLE:
            raise ImportError("azure-discovery not available")
        
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
        
        print(f"\n✓ Exported {len(nodes)} nodes and {len(relationships)} relationships")
        print(f"  Snapshot: {output_path}")
    
    async def load_snapshot(
        self,
        snapshot_path: Path
    ) -> Tuple[List[ResourceNode], List[DiscoveryRelationship]]:
        """Load snapshot from JSON file.
        
        Args:
            snapshot_path: Path to JSON snapshot file
        
        Returns:
            Tuple of (nodes, relationships)
        """
        if not AZURE_DISCOVERY_AVAILABLE:
            raise ImportError("azure-discovery not available")
        
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")
        
        with open(snapshot_path) as f:
            data = json.load(f)
        
        # Reconstruct Pydantic models
        nodes = [ResourceNode(**n) for n in data['nodes']]
        relationships = [DiscoveryRelationship(**r) for r in data['relationships']]
        
        metadata = data.get('metadata', {})
        print(f"\n✓ Loaded snapshot from {snapshot_path}")
        print(f"  Created: {metadata.get('created_at', 'unknown')}")
        print(f"  Nodes: {len(nodes)}")
        print(f"  Relationships: {len(relationships)}")
        
        return nodes, relationships
    
    async def seed_from_snapshot(
        self,
        snapshot_path: Path,
        state_manager: StateManager,
        clear_existing: bool = False
    ):
        """Seed mazure state from saved snapshot.
        
        Args:
            snapshot_path: Path to JSON snapshot file
            state_manager: StateManager instance
            clear_existing: If True, clear existing state before seeding
        """
        if clear_existing:
            await self._clear_state()
        
        nodes, relationships = await self.load_snapshot(snapshot_path)
        
        seeder = DiscoveryStateSeeder(state_manager)
        
        print(f"\nSeeding mazure state...")
        
        # Import nodes
        for i, node in enumerate(nodes, 1):
            try:
                if not node.id.startswith('graph://'):
                    await seeder._import_arm_resource(node)
                else:
                    await seeder._import_graph_object(node)
                
                if i % 50 == 0:
                    print(f"  Imported {i}/{len(nodes)} resources...")
            except Exception as e:
                print(f"  Error importing {node.id}: {e}")
        
        # Import relationships
        for i, rel in enumerate(relationships, 1):
            try:
                await seeder._import_relationship(rel)
                
                if i % 100 == 0:
                    print(f"  Imported {i}/{len(relationships)} relationships...")
            except Exception as e:
                print(f"  Error importing relationship: {e}")
        
        print(f"\n✓ Seeded {len(nodes)} resources and {len(relationships)} relationships")
    
    async def _clear_state(self):
        """Clear all existing mock state."""
        print("\nClearing existing state...")
        GenericResource.objects.delete()
        ResourceRelationship.objects.delete()
        print("  ✓ State cleared")
    
    def list_snapshots(self, fixtures_dir: Path) -> List[Dict[str, Any]]:
        """List available snapshot fixtures.
        
        Args:
            fixtures_dir: Directory containing snapshot JSON files
        
        Returns:
            List of snapshot metadata dicts
        """
        if not fixtures_dir.exists():
            return []
        
        snapshots = []
        for snapshot_file in fixtures_dir.glob('**/*.json'):
            try:
                with open(snapshot_file) as f:
                    data = json.load(f)
                    snapshots.append({
                        'path': str(snapshot_file.relative_to(fixtures_dir)),
                        'absolute_path': str(snapshot_file),
                        'metadata': data.get('metadata', {})
                    })
            except Exception as e:
                print(f"Warning: Could not read {snapshot_file}: {e}")
        
        return snapshots
