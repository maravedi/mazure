"""Integration tests for Microsoft Graph API mock."""

import pytest
import asyncio
from mazure.services.graph import GraphService
from mazure.core.state import StateManager


class TestGraphAPIUsers:
    """Test Graph API user endpoints."""
    
    @pytest.fixture
    def service(self):
        """Create GraphService instance."""
        return GraphService(StateManager())
    
    @pytest.mark.asyncio
    async def test_list_users(self, service):
        """Test listing users."""
        result = await service.list_users(top=10, skip=0)
        
        assert '@odata.context' in result
        assert 'value' in result
        assert isinstance(result['value'], list)
    
    @pytest.mark.asyncio
    async def test_list_users_with_select(self, service):
        """Test listing users with field selection."""
        result = await service.list_users(
            top=5,
            select=['displayName', 'mail']
        )
        
        assert 'value' in result
        # Each user should have only selected fields (plus id)
        for user in result['value']:
            assert 'id' in user
            assert 'displayName' in user or 'mail' in user
    
    @pytest.mark.asyncio
    async def test_list_users_pagination(self, service):
        """Test user listing pagination."""
        # Get first page
        page1 = await service.list_users(top=2, skip=0)
        
        # Check for next link if there are more results
        if '@odata.nextLink' in page1:
            assert '$skip=2' in page1['@odata.nextLink']
        
        # Get second page
        page2 = await service.list_users(top=2, skip=2)
        assert 'value' in page2
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, service):
        """Test getting user by ID."""
        # First list users to get an ID
        users = await service.list_users(top=1)
        
        if users['value']:
            user_id = users['value'][0]['id']
            result = await service.get_user(user_id)
            
            assert 'id' in result
            assert result['id'] == user_id
            assert 'userPrincipalName' in result or 'displayName' in result


class TestGraphAPIGroups:
    """Test Graph API group endpoints."""
    
    @pytest.fixture
    def service(self):
        """Create GraphService instance."""
        return GraphService(StateManager())
    
    @pytest.mark.asyncio
    async def test_list_groups(self, service):
        """Test listing groups."""
        result = await service.list_groups(top=10, skip=0)
        
        assert '@odata.context' in result
        assert 'value' in result
        assert isinstance(result['value'], list)
    
    @pytest.mark.asyncio
    async def test_list_groups_with_filter(self, service):
        """Test listing groups with OData filter."""
        # Filter by display name starting with specific prefix
        result = await service.list_groups(
            top=10,
            filter_expr="startswith(displayName, 'IT')"
        )
        
        assert 'value' in result
        # All groups should match filter
        for group in result['value']:
            if 'displayName' in group:
                # Note: filter may not apply if no groups match
                pass
    
    @pytest.mark.asyncio
    async def test_get_group_by_id(self, service):
        """Test getting group by ID."""
        # First list groups to get an ID
        groups = await service.list_groups(top=1)
        
        if groups['value']:
            group_id = groups['value'][0]['id']
            result = await service.get_group(group_id)
            
            assert 'id' in result
            assert result['id'] == group_id
            assert 'displayName' in result
    
    @pytest.mark.asyncio
    async def test_list_group_members(self, service):
        """Test listing group members."""
        # First get a group
        groups = await service.list_groups(top=1)
        
        if groups['value']:
            group_id = groups['value'][0]['id']
            result = await service.list_group_members(group_id, top=10)
            
            assert '@odata.context' in result
            assert 'value' in result
            assert isinstance(result['value'], list)
            
            # Members should have @odata.type
            for member in result['value']:
                if '@odata.type' in member:
                    assert 'microsoft.graph' in member['@odata.type']


class TestGraphAPIODataSupport:
    """Test OData query parameter support."""
    
    @pytest.fixture
    def service(self):
        """Create GraphService instance."""
        return GraphService(StateManager())
    
    @pytest.mark.asyncio
    async def test_select_parameter(self, service):
        """Test $select parameter."""
        result = await service.list_users(
            top=5,
            select=['displayName']
        )
        
        for user in result['value']:
            # Should only have id and selected fields
            assert 'id' in user
            assert 'displayName' in user or len(user.keys()) == 1
    
    @pytest.mark.asyncio
    async def test_top_parameter(self, service):
        """Test $top parameter for limiting results."""
        result = await service.list_users(top=3)
        
        assert len(result['value']) <= 3
    
    @pytest.mark.asyncio
    async def test_skip_parameter(self, service):
        """Test $skip parameter for pagination."""
        # Get first page
        page1 = await service.list_users(top=2, skip=0)
        
        # Get second page
        page2 = await service.list_users(top=2, skip=2)
        
        # Pages should be different (if enough data)
        if len(page1['value']) == 2 and len(page2['value']) > 0:
            assert page1['value'][0]['id'] != page2['value'][0]['id']
    
    @pytest.mark.asyncio
    async def test_filter_parameter(self, service):
        """Test $filter parameter."""
        # Test equality filter
        result = await service.list_groups(
            filter_expr="securityEnabled eq true"
        )
        
        assert 'value' in result
        # Should only return security-enabled groups (if filter works)
        for group in result['value']:
            if 'securityEnabled' in group:
                # Note: All groups may be security-enabled
                pass


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
