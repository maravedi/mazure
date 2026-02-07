"""Example usage of Resource Graph and Microsoft Graph API mocks.

Demonstrates how to use the newly implemented query engines with
discovery-seeded data.
"""

import asyncio
from pathlib import Path

# These would normally be imported from mazure
from mazure.services.resource_graph import ResourceGraphService
from mazure.services.graph import GraphService
from mazure.core.state import StateManager
from mazure.scenarios.snapshot_manager import SnapshotManager
from mazure.codegen.response_synthesizer import ResponseSynthesizer


async def example_resource_graph_queries():
    """Example Resource Graph queries."""
    print("\n=== Resource Graph Query Examples ===")
    
    service = ResourceGraphService(StateManager())
    subscriptions = ['mock-subscription-id']
    
    # Example 1: List all VMs
    print("\n1. List all virtual machines:")
    query = "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | take 5"
    result = await service.query(subscriptions, query)
    print(f"   Found {result['count']} VMs (of {result['totalRecords']} total)")
    
    # Example 2: Project specific fields
    print("\n2. Get VM names and locations:")
    query = "Resources | where type =~ 'Microsoft.Compute/virtualMachines' | project name, location"
    result = await service.query(subscriptions, query)
    for resource in result['data'][:3]:
        print(f"   - {resource.get('name')} in {resource.get('location')}")
    
    # Example 3: Filter by location
    print("\n3. Resources in East US:")
    query = "Resources | where location == 'eastus' | summarize count() by type"
    result = await service.query(subscriptions, query)
    for item in result['data'][:5]:
        print(f"   - {item['type']}: {item['count']} resources")
    
    # Example 4: Count resources by type
    print("\n4. Resource counts by type:")
    query = "Resources | summarize count() by type"
    result = await service.query(subscriptions, query)
    for item in sorted(result['data'], key=lambda x: x['count'], reverse=True)[:5]:
        print(f"   - {item['type']}: {item['count']}")
    
    # Example 5: Tag filtering
    print("\n5. Resources tagged with environment=production:")
    query = "Resources | where tags['environment'] == 'production' | take 5"
    result = await service.query(subscriptions, query)
    print(f"   Found {result['count']} production resources")


async def example_graph_api_queries():
    """Example Microsoft Graph API queries."""
    print("\n=== Microsoft Graph API Examples ===")
    
    service = GraphService(StateManager())
    
    # Example 1: List users
    print("\n1. List first 5 users:")
    result = await service.list_users(top=5, skip=0)
    print(f"   Found {len(result.get('value', []))} users")
    for user in result.get('value', []):
        print(f"   - {user.get('displayName')} ({user.get('userPrincipalName')})")
    
    # Example 2: Filter users
    print("\n2. Users with displayName starting with 'John':")
    result = await service.list_users(
        top=10,
        filter_expr="startswith(displayName,'John')"
    )
    print(f"   Found {len(result.get('value', []))} matching users")
    
    # Example 3: Select specific fields
    print("\n3. Get user emails only:")
    result = await service.list_users(
        top=3,
        select=['displayName', 'mail']
    )
    for user in result.get('value', []):
        print(f"   - {user.get('displayName')}: {user.get('mail')}")
    
    # Example 4: List groups
    print("\n4. List security groups:")
    result = await service.list_groups(top=5)
    print(f"   Found {len(result.get('value', []))} groups")
    for group in result.get('value', []):
        print(f"   - {group.get('displayName')} (Security: {group.get('securityEnabled')})")
    
    # Example 5: Group members (requires seeded relationships)
    print("\n5. Get group members:")
    # This would work if you have a real group ID from seeded data
    # result = await service.list_group_members('group-id-here', top=10)
    # for member in result.get('value', []):
    #     print(f"   - {member.get('displayName')} ({member.get('@odata.type')})")
    print("   (Requires seeded relationship data)")


async def example_snapshot_workflow():
    """Example workflow: seed from snapshot, then query."""
    print("\n=== Snapshot Workflow Example ===")
    
    # 1. Load a snapshot
    print("\n1. Loading snapshot...")
    snapshot_path = Path('fixtures/prod-topology.json')
    
    if not snapshot_path.exists():
        print("   ⚠ Snapshot file not found. Create one with:")
        print("   mazure seed from-azure <tenant-id> --output fixtures/prod-topology.json")
        return
    
    manager = SnapshotManager()
    nodes, relationships = await manager.load_snapshot(snapshot_path)
    print(f"   ✓ Loaded {len(nodes)} nodes and {len(relationships)} relationships")
    
    # 2. Seed into state
    print("\n2. Seeding state...")
    await manager.seed_from_snapshot(snapshot_path, StateManager(), clear_existing=True)
    print("   ✓ State seeded")
    
    # 3. Run queries
    print("\n3. Running queries against seeded data...")
    await example_resource_graph_queries()
    await example_graph_api_queries()


async def example_response_synthesis():
    """Example response synthesis from patterns."""
    print("\n=== Response Synthesis Example ===")
    
    # Load historical data from snapshot
    snapshot_path = Path('fixtures/prod-topology.json')
    if not snapshot_path.exists():
        print("   ⚠ Snapshot file not found")
        return
    
    manager = SnapshotManager()
    nodes, _ = await manager.load_snapshot(snapshot_path)
    
    # Initialize synthesizer
    print("\n1. Analyzing patterns from historical data...")
    synth = ResponseSynthesizer(nodes)
    stats = synth.get_statistics()
    print(f"   ✓ Analyzed {stats['total_resources']} resources")
    print(f"   ✓ Found patterns for {stats['types_with_patterns']} resource types")
    
    # Generate realistic VMs
    print("\n2. Generating realistic virtual machines...")
    vms = synth.synthesize_batch(
        resource_type='Microsoft.Compute/virtualMachines',
        count=3,
        override_tags={'environment': 'test', 'generated': 'true'}
    )
    
    for vm in vms:
        print(f"   - {vm['name']} in {vm['location']}")
        print(f"     Properties: {list(vm['properties'].keys())[:3]}...")
        print(f"     Tags: {vm['tags']}")
    
    # Get statistics for a type
    print("\n3. Common patterns for VMs:")
    locations = synth.get_common_locations_for_type('Microsoft.Compute/virtualMachines')
    print(f"   Common locations: {', '.join(locations[:3])}")
    
    tags = synth.get_common_tags_for_type('Microsoft.Compute/virtualMachines')
    print(f"   Common tags: {', '.join(list(tags.keys())[:3])}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Azure Discovery Integration - Query Examples")
    print("=" * 60)
    
    # Note: These examples assume you have:
    # 1. MongoDB running (for state storage)
    # 2. A snapshot file seeded with discovery data
    # 3. The mazure package installed
    
    try:
        # Run examples
        await example_resource_graph_queries()
        await example_graph_api_queries()
        # await example_snapshot_workflow()  # Uncomment when snapshot exists
        # await example_response_synthesis()  # Uncomment when snapshot exists
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. MongoDB is running")
        print("  2. You have seeded data (mazure seed from-azure ...)")
        print("  3. The mazure package is installed")


if __name__ == '__main__':
    asyncio.run(main())
