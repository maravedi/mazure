"""Integration tests for Microsoft Graph API."""

import pytest
import asyncio
from mazure.services.graph import GraphService
from mazure.core.state import StateManager


@pytest.fixture
def service():
    """Create GraphService instance."""
    return GraphService(StateManager())


@pytest.mark.asyncio
class TestGraphAPIIntegration:
    """Integration tests for Microsoft Graph API."""
    
    async def test_list_users(self, service):
        """Test listing users."""
        result = await service.list_users(top=10)
        assert '@odata.context' in result
        assert 'value' in result
        assert isinstance(result['value'], list)
    
    async def test_list_users_with_filter(self, service):
        """Test user list with $filter."""
        result = await service.list_users(
            top=10,
            filter_expr="startswith(displayName,'Test')"
        )
        assert 'value' in result
    
    async def test_list_users_with_select(self, service):
        """Test user list with $select."""
        result = await service.list_users(
            top=5,
            select=['displayName', 'mail']
        )
        assert 'value' in result
        if result['value']:
            for user in result['value']:
                # Should have id plus selected fields
                assert 'id' in user
                assert 'displayName' in user
    
    async def test_pagination(self, service):
        """Test pagination with $top and $skip."""
        result = await service.list_users(top=5, skip=0)
        assert 'value' in result
        assert len(result['value']) <= 5
    
    async def test_list_groups(self, service):
        """Test listing groups."""
        result = await service.list_groups(top=10)
        assert '@odata.context' in result
        assert 'value' in result
        assert isinstance(result['value'], list)
    
    async def test_group_members(self, service):
        """Test getting group members."""
        # First get a group
        groups = await service.list_groups(top=1)
        if groups['value']:
            group_id = groups['value'][0]['id']
            result = await service.list_group_members(group_id, top=10)
            assert 'value' in result
            assert isinstance(result['value'], list)
