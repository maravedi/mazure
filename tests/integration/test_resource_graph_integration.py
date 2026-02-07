"""Integration tests for Resource Graph query engine."""

import pytest
import asyncio
from mazure.services.resource_graph import ResourceGraphService
from mazure.core.state import StateManager


@pytest.fixture
def service():
    """Create ResourceGraphService instance."""
    return ResourceGraphService(StateManager())


@pytest.mark.asyncio
class TestResourceGraphIntegration:
    """Integration tests for Resource Graph queries."""
    
    async def test_basic_query(self, service):
        """Test basic Resources query."""
        result = await service.query(
            subscriptions=['test-sub'],
            query='Resources | take 5'
        )
        assert 'data' in result
        assert 'count' in result
        assert 'totalRecords' in result
    
    async def test_where_type_filter(self, service):
        """Test WHERE clause with type filter."""
        result = await service.query(
            subscriptions=['test-sub'],
            query="Resources | where type =~ 'Microsoft.Compute/virtualMachines'"
        )
        assert 'data' in result
        for resource in result['data']:
            assert resource['type'].lower() == 'microsoft.compute/virtualmachines'
    
    async def test_project_fields(self, service):
        """Test PROJECT operator."""
        result = await service.query(
            subscriptions=['test-sub'],
            query='Resources | project name, type, location | take 5'
        )
        assert 'data' in result
        if result['data']:
            for item in result['data']:
                assert 'name' in item
                assert 'type' in item
                assert 'location' in item
                # Should only have projected fields
                assert len(item) <= 3
    
    async def test_summarize_count(self, service):
        """Test SUMMARIZE count by field."""
        result = await service.query(
            subscriptions=['test-sub'],
            query='Resources | summarize count() by type'
        )
        assert 'data' in result
        if result['data']:
            for item in result['data']:
                assert 'type' in item
                assert 'count' in item
                assert isinstance(item['count'], int)
    
    async def test_pagination(self, service):
        """Test pagination with $skip and $top."""
        result = await service.query(
            subscriptions=['test-sub'],
            query='Resources',
            options={'$skip': 0, '$top': 5}
        )
        assert result['count'] <= 5
    
    async def test_location_filter(self, service):
        """Test WHERE with location filter."""
        result = await service.query(
            subscriptions=['test-sub'],
            query="Resources | where location == 'eastus'"
        )
        assert 'data' in result
        for resource in result['data']:
            assert resource.get('location') == 'eastus'
    
    async def test_complex_query(self, service):
        """Test complex multi-operator query."""
        result = await service.query(
            subscriptions=['test-sub'],
            query="""
                Resources 
                | where type =~ 'Microsoft.Compute/virtualMachines'
                | project name, location
                | take 10
            """
        )
        assert 'data' in result
        assert result['count'] <= 10
