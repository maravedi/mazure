"""Integration tests for Azure Discovery seeding functionality.

These tests demonstrate how to use discovery integration features.
Note: Requires MongoDB connection and azure-discovery package.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

try:
    from azure_discovery.adt_types import ResourceNode, ResourceRelationship as DiscoveryRelationship
    from mazure.seeding.discovery_importer import DiscoveryStateSeeder
    from mazure.scenarios.snapshot_manager import SnapshotManager
    from mazure.core.state import StateManager, GenericResource
    from mazure.core.relationships import ResourceRelationship
    DISCOVERY_AVAILABLE = True
except ImportError:
    DISCOVERY_AVAILABLE = False


@pytest.mark.skipif(not DISCOVERY_AVAILABLE, reason="azure-discovery not installed")
class TestDiscoverySeeding:
    """Test discovery state seeding functionality."""
    
    @pytest.fixture
    def sample_arm_node(self):
        """Create sample ARM resource node."""
        return ResourceNode(
            id="/subscriptions/sub-123/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/test-vm",
            name="test-vm",
            type="Microsoft.Compute/virtualMachines",
            subscription_id="sub-123",
            resource_group="test-rg",
            location="eastus",
            properties={
                "vmSize": "Standard_D2s_v3",
                "osProfile": {"computerName": "test-vm"},
                "provisioningState": "Succeeded"
            },
            tags={"environment": "test", "owner": "eng-team"}
        )
    
    @pytest.fixture
    def sample_graph_node(self):
        """Create sample Entra ID user node."""
        return ResourceNode(
            id="graph://user/12345-67890",
            name="john.doe@contoso.com",
            type="Microsoft.Graph/User",
            subscription_id="Tenant",
            properties={
                "userPrincipalName": "john.doe@contoso.com",
                "displayName": "John Doe",
                "jobTitle": "Engineer",
                "mail": "john.doe@contoso.com"
            },
            tags={"graph_id": "12345-67890"}
        )
    
    @pytest.fixture
    def sample_relationship(self, sample_arm_node):
        """Create sample relationship."""
        return DiscoveryRelationship(
            source_id=sample_arm_node.id,
            target_id="/subscriptions/sub-123/resourceGroups/test-rg/providers/Microsoft.Network/networkInterfaces/test-nic",
            relation_type="depends_on",
            weight=1.0
        )
    
    @pytest.mark.asyncio
    async def test_import_arm_resource(self, sample_arm_node):
        """Test importing ARM resource into mazure state."""
        seeder = DiscoveryStateSeeder(StateManager())
        
        # Import resource
        resource = await seeder._import_arm_resource(sample_arm_node)
        
        # Verify resource was created
        assert resource is not None
        assert resource.name == "test-vm"
        assert resource.resource_type == "Microsoft.Compute/virtualMachines"
        assert resource.subscription_id == "sub-123"
        assert resource.resource_group == "test-rg"
        assert resource.location == "eastus"
        assert resource.properties["vmSize"] == "Standard_D2s_v3"
        assert resource.tags["environment"] == "test"
        
        # Cleanup
        resource.delete()
    
    @pytest.mark.asyncio
    async def test_import_graph_object(self, sample_graph_node):
        """Test importing Graph/Entra object."""
        seeder = DiscoveryStateSeeder(StateManager())
        
        # Import Graph object
        resource = await seeder._import_graph_object(sample_graph_node)
        
        # Verify stored as pseudo-resource
        assert resource is not None
        assert resource.subscription_id == "Tenant"
        assert resource.resource_group == "EntraID"
        assert resource.type == "Microsoft.Graph/User"
        assert resource.properties["userPrincipalName"] == "john.doe@contoso.com"
        
        # Cleanup
        resource.delete()
    
    @pytest.mark.asyncio
    async def test_import_relationship(self, sample_relationship):
        """Test importing resource relationship."""
        seeder = DiscoveryStateSeeder(StateManager())
        
        # Import relationship
        rel = await seeder._import_relationship(sample_relationship)
        
        # Verify relationship created
        assert rel is not None
        assert rel.relation_type == "depends_on"
        assert rel.weight == 1.0
        
        # Query relationship
        found_rels = ResourceRelationship.find_outbound(sample_relationship.source_id)
        assert len(found_rels) > 0
        assert any(r.target_id == sample_relationship.target_id for r in found_rels)
        
        # Cleanup
        rel.delete()
    
    @pytest.mark.asyncio
    async def test_snapshot_export_load(self, sample_arm_node, sample_graph_node, sample_relationship, tmp_path):
        """Test exporting and loading snapshots."""
        manager = SnapshotManager()
        snapshot_path = tmp_path / "test-snapshot.json"
        
        # Export snapshot
        await manager.export_snapshot(
            nodes=[sample_arm_node, sample_graph_node],
            relationships=[sample_relationship],
            output_path=snapshot_path,
            metadata={"test": "snapshot"}
        )
        
        # Verify file created
        assert snapshot_path.exists()
        
        # Load snapshot
        nodes, rels = await manager.load_snapshot(snapshot_path)
        
        # Verify loaded data
        assert len(nodes) == 2
        assert len(rels) == 1
        assert nodes[0].id == sample_arm_node.id
        assert nodes[1].id == sample_graph_node.id
        assert rels[0].source_id == sample_relationship.source_id
    
    @pytest.mark.asyncio
    async def test_seed_from_snapshot(self, sample_arm_node, sample_graph_node, sample_relationship, tmp_path):
        """Test seeding mazure state from snapshot."""
        manager = SnapshotManager()
        snapshot_path = tmp_path / "test-snapshot.json"
        
        # Create and export snapshot
        await manager.export_snapshot(
            nodes=[sample_arm_node, sample_graph_node],
            relationships=[sample_relationship],
            output_path=snapshot_path
        )
        
        # Seed from snapshot
        await manager.seed_from_snapshot(
            snapshot_path,
            StateManager(),
            clear_existing=True
        )
        
        # Verify resources were seeded
        arm_resource = GenericResource.objects(
            name="test-vm",
            resource_type="Microsoft.Compute/virtualMachines"
        ).first()
        assert arm_resource is not None
        assert arm_resource.location == "eastus"
        
        graph_resource = GenericResource.objects(
            name="john.doe@contoso.com",
            resource_type="Microsoft.Graph/User"
        ).first()
        assert graph_resource is not None
        assert graph_resource.subscription_id == "Tenant"
        
        # Verify relationship was seeded
        rels = ResourceRelationship.objects(source_id=sample_arm_node.id)
        assert rels.count() > 0
        
        # Cleanup
        GenericResource.objects.delete()
        ResourceRelationship.objects.delete()


@pytest.mark.skipif(not DISCOVERY_AVAILABLE, reason="azure-discovery not installed")
class TestSnapshotManagement:
    """Test snapshot fixture management."""
    
    @pytest.mark.asyncio
    async def test_list_snapshots(self, tmp_path):
        """Test listing snapshot fixtures."""
        manager = SnapshotManager()
        
        # Create test snapshots
        (tmp_path / "snap1.json").write_text('{"metadata": {"node_count": 5}, "nodes": [], "relationships": []}')
        (tmp_path / "snap2.json").write_text('{"metadata": {"node_count": 10}, "nodes": [], "relationships": []}')
        
        # List snapshots
        snapshots = manager.list_snapshots(tmp_path)
        
        # Verify found both
        assert len(snapshots) == 2
        assert any('snap1.json' in s['path'] for s in snapshots)
        assert any('snap2.json' in s['path'] for s in snapshots)
    
    @pytest.mark.asyncio
    async def test_snapshot_metadata(self, tmp_path):
        """Test snapshot metadata preservation."""
        manager = SnapshotManager()
        snapshot_path = tmp_path / "meta-test.json"
        
        # Create sample node
        node = ResourceNode(
            id="/test/resource",
            name="test",
            type="Test.Resource",
            subscription_id="sub"
        )
        
        # Export with custom metadata
        await manager.export_snapshot(
            nodes=[node],
            relationships=[],
            output_path=snapshot_path,
            metadata={
                "environment": "production",
                "description": "Test snapshot",
                "tags": ["test", "demo"]
            }
        )
        
        # List and verify metadata
        snapshots = manager.list_snapshots(tmp_path)
        snap = next(s for s in snapshots if 'meta-test.json' in s['path'])
        
        assert snap['metadata']['environment'] == "production"
        assert snap['metadata']['description'] == "Test snapshot"
        assert 'test' in snap['metadata']['tags']


# Example usage in actual integration tests
@pytest.mark.integration
@pytest.mark.skipif(not DISCOVERY_AVAILABLE, reason="azure-discovery not installed")
class TestIntegrationWithSnapshots:
    """Example integration tests using snapshot fixtures."""
    
    @pytest.fixture
    async def loaded_snapshot(self, tmp_path):
        """Fixture that loads a test snapshot."""
        # Create test snapshot
        vm_node = ResourceNode(
            id="/subscriptions/test/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",
            name="vm1",
            type="Microsoft.Compute/virtualMachines",
            subscription_id="test-sub",
            resource_group="rg",
            location="eastus",
            properties={"vmSize": "Standard_B2s"}
        )
        
        snapshot_path = tmp_path / "test.json"
        manager = SnapshotManager()
        
        await manager.export_snapshot([vm_node], [], snapshot_path)
        await manager.seed_from_snapshot(snapshot_path, StateManager(), clear_existing=True)
        
        yield
        
        # Cleanup
        GenericResource.objects.delete()
        ResourceRelationship.objects.delete()
    
    @pytest.mark.asyncio
    async def test_query_seeded_resources(self, loaded_snapshot):
        """Test querying resources from loaded snapshot."""
        # Query the VM that was seeded
        vm = GenericResource.objects(
            name="vm1",
            resource_type="Microsoft.Compute/virtualMachines"
        ).first()
        
        assert vm is not None
        assert vm.location == "eastus"
        assert vm.properties["vmSize"] == "Standard_B2s"
