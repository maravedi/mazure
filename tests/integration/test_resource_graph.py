"""Integration tests for Resource Graph query engine."""

import pytest
import asyncio
from mazure.services.resource_graph import ResourceGraphService
from mazure.core.state import StateManager


class TestResourceGraphQueries:
    """Test Resource Graph KQL query execution."""
    
    @pytest.fixture
    def service(self):
        """Create ResourceGraphService instance."""
        return ResourceGraphService(StateManager())
    
    @pytest.mark.asyncio
    async def test_basic_resources_query(self, service):
        """Test basic Resources table query."""
        query = "Resources"
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        assert 'count' in result
        assert 'totalRecords' in result
        assert isinstance(result['data'], list)
    
    @pytest.mark.asyncio
    async def test_where_type_filter(self, service):
        """Test WHERE clause with type filter."""
        query = "Resources | where type =~ 'Microsoft.Compute/virtualMachines'"
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        # All returned resources should be VMs
        for resource in result['data']:
            assert resource['type'].lower() == 'microsoft.compute/virtualmachines'
    
    @pytest.mark.asyncio
    async def test_project_fields(self, service):
        """Test PROJECT clause for field selection."""
        query = "Resources | project name, type, location"
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        # Each resource should only have projected fields
        for resource in result['data']:
            assert set(resource.keys()) == {'name', 'type', 'location'}
    
    @pytest.mark.asyncio
    async def test_take_limit(self, service):
        """Test TAKE clause for limiting results."""
        query = "Resources | take 5"
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        assert len(result['data']) <= 5
    
    @pytest.mark.asyncio
    async def test_summarize_count(self, service):
        """Test SUMMARIZE clause for aggregation."""
        query = "Resources | summarize count() by type"
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        # Results should have type and count fields
        for item in result['data']:
            assert 'type' in item
            assert 'count' in item
            assert isinstance(item['count'], int)
    
    @pytest.mark.asyncio
    async def test_chained_operators(self, service):
        """Test multiple operators chained together."""
        query = (
            "Resources | "
            "where type =~ 'Microsoft.Compute/virtualMachines' | "
            "project name, location | "
            "take 10"
        )
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        assert len(result['data']) <= 10
        for resource in result['data']:
            assert set(resource.keys()) == {'name', 'location'}
    
    @pytest.mark.asyncio
    async def test_resource_containers(self, service):
        """Test ResourceContainers table query."""
        query = "ResourceContainers"
        subscriptions = ["test-subscription"]
        
        result = await service.query(subscriptions, query)
        
        assert 'data' in result
        # Should include subscription and resource groups
        types = {r['type'] for r in result['data']}
        assert 'microsoft.resources/subscriptions' in types or len(result['data']) == 0


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
