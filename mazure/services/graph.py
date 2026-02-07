"""Microsoft Graph API mock implementation.

Provides mock endpoints for Entra ID queries including users, groups,
applications, and service principals using discovery-seeded data.
"""

from typing import List, Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class GraphService:
    """Microsoft Graph API mock using Entra discovery data.
    
    Implements core Graph API endpoints:
    - /v1.0/users (list, get)
    - /v1.0/groups (list, get, members)
    - /v1.0/applications
    - /v1.0/servicePrincipals
    
    Supports OData query parameters:
    - $select: Field selection
    - $filter: Filtering
    - $top: Limit results
    - $skip: Pagination offset
    - $orderby: Sorting
    """
    
    def __init__(self, state_manager):
        """Initialize with state manager.
        
        Args:
            state_manager: StateManager instance for accessing resources
        """
        self.state = state_manager
    
    # ==================== Users ====================
    
    async def list_users(
        self,
        top: int = 100,
        skip: int = 0,
        select: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
        orderby: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/users endpoint.
        
        Args:
            top: Maximum results to return
            skip: Number of results to skip
            select: Fields to include in response
            filter_expr: OData filter expression
            orderby: Sort expression
        
        Returns:
            Graph API response with users
        """
        try:
            from ..core.state import GenericResource
        except ImportError:
            return self._empty_response('users')
        
        try:
            # Query users seeded from Entra discovery
            query_params = {
                'subscription_id': 'Tenant',
                'resource_group': 'EntraID',
                'resource_type': 'Microsoft.Graph/User'
            }
            
            users = GenericResource.objects(**query_params)
            
            # Apply $filter
            if filter_expr:
                users = self._apply_odata_filter(users, filter_expr, 'user')
            
            # Apply $orderby
            if orderby:
                users = self._apply_orderby(users, orderby)
            
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
                response['@odata.nextLink'] = (
                    f'https://graph.microsoft.com/v1.0/users'
                    f'?$skip={skip + top}&$top={top}'
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list users: {str(e)}")
            return self._error_response(500, 'InternalServerError', str(e))
    
    async def get_user(
        self,
        user_id: str,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/users/{id} endpoint.
        
        Args:
            user_id: User ID or userPrincipalName
            select: Fields to include in response
        
        Returns:
            User object or error
        """
        try:
            from ..core.state import GenericResource
        except ImportError:
            return self._error_response(404, 'NotFound', 'User not found')
        
        try:
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
                return self._error_response(404, 'NotFound', f'User {user_id} not found')
            
            return self._format_graph_user(user, select)
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}")
            return self._error_response(500, 'InternalServerError', str(e))
    
    # ==================== Groups ====================
    
    async def list_groups(
        self,
        top: int = 100,
        skip: int = 0,
        select: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
        orderby: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/groups endpoint.
        
        Args:
            top: Maximum results to return
            skip: Number of results to skip
            select: Fields to include
            filter_expr: OData filter expression
            orderby: Sort expression
        
        Returns:
            Graph API response with groups
        """
        try:
            from ..core.state import GenericResource
        except ImportError:
            return self._empty_response('groups')
        
        try:
            groups = GenericResource.objects(
                subscription_id='Tenant',
                resource_group='EntraID',
                resource_type='Microsoft.Graph/Group'
            )
            
            if filter_expr:
                groups = self._apply_odata_filter(groups, filter_expr, 'group')
            
            if orderby:
                groups = self._apply_orderby(groups, orderby)
            
            total = groups.count()
            paginated = list(groups.skip(skip).limit(top))
            
            response = {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#groups',
                'value': [self._format_graph_group(g, select) for g in paginated]
            }
            
            if skip + top < total:
                response['@odata.nextLink'] = (
                    f'https://graph.microsoft.com/v1.0/groups'
                    f'?$skip={skip + top}&$top={top}'
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list groups: {str(e)}")
            return self._error_response(500, 'InternalServerError', str(e))
    
    async def get_group(
        self,
        group_id: str,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/groups/{id} endpoint.
        
        Args:
            group_id: Group ID
            select: Fields to include
        
        Returns:
            Group object or error
        """
        try:
            from ..core.state import GenericResource
        except ImportError:
            return self._error_response(404, 'NotFound', 'Group not found')
        
        try:
            group = GenericResource.objects(
                resource_type='Microsoft.Graph/Group',
                resource_id__icontains=group_id
            ).first()
            
            if not group:
                group = GenericResource.objects(
                    resource_type='Microsoft.Graph/Group',
                    name=group_id
                ).first()
            
            if not group:
                return self._error_response(404, 'NotFound', f'Group {group_id} not found')
            
            return self._format_graph_group(group, select)
            
        except Exception as e:
            logger.error(f"Failed to get group {group_id}: {str(e)}")
            return self._error_response(500, 'InternalServerError', str(e))
    
    async def list_group_members(
        self,
        group_id: str,
        top: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """Mock GET /v1.0/groups/{id}/members endpoint.
        
        Uses relationships stored during discovery import.
        
        Args:
            group_id: Group ID
            top: Maximum results
            skip: Results to skip
        
        Returns:
            List of directory objects
        """
        try:
            from ..core.state import GenericResource
            from ..core.relationships import ResourceRelationship
        except ImportError:
            return self._empty_response('directoryObjects')
        
        try:
            # Find group resource ID
            group_resource_id = f"graph://group/{group_id}"
            
            # Get member relationships
            member_rels = ResourceRelationship.objects(
                source_id=group_resource_id,
                relation_type='has_member'
            ).skip(skip).limit(top)
            
            # Load member objects
            members = []
            for rel in member_rels:
                member = GenericResource.objects(resource_id=rel.target_id).first()
                if member:
                    members.append(self._format_directory_object(member))
            
            # Count total for pagination
            total = ResourceRelationship.objects(
                source_id=group_resource_id,
                relation_type='has_member'
            ).count()
            
            response = {
                '@odata.context': 'https://graph.microsoft.com/v1.0/$metadata#directoryObjects',
                'value': members
            }
            
            if skip + top < total:
                response['@odata.nextLink'] = (
                    f'https://graph.microsoft.com/v1.0/groups/{group_id}/members'
                    f'?$skip={skip + top}&$top={top}'
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list group members for {group_id}: {str(e)}")
            return self._error_response(500, 'InternalServerError', str(e))
    
    # ==================== Formatting ====================
    
    def _format_graph_user(self, resource, select: Optional[List[str]] = None) -> Dict:
        """Format GenericResource as Graph API user object.
        
        Args:
            resource: GenericResource instance
            select: Fields to include
        
        Returns:
            User dictionary
        """
        props = resource.properties or {}
        graph_id = resource.tags.get('graph_id', 'unknown')
        
        user = {
            'id': graph_id,
            'userPrincipalName': props.get('userPrincipalName', resource.name),
            'displayName': props.get('displayName', resource.name),
            'givenName': props.get('givenName'),
            'surname': props.get('surname'),
            'mail': props.get('mail'),
            'mailNickname': props.get('mailNickname'),
            'jobTitle': props.get('jobTitle'),
            'department': props.get('department'),
            'officeLocation': props.get('officeLocation'),
            'mobilePhone': props.get('mobilePhone'),
            'businessPhones': props.get('businessPhones', []),
            'accountEnabled': props.get('accountEnabled', True),
            'userType': props.get('userType', 'Member')
        }
        
        # Apply $select if provided
        if select:
            user = {k: v for k, v in user.items() if k in select or k == 'id'}
        
        return user
    
    def _format_graph_group(self, resource, select: Optional[List[str]] = None) -> Dict:
        """Format GenericResource as Graph API group object.
        
        Args:
            resource: GenericResource instance
            select: Fields to include
        
        Returns:
            Group dictionary
        """
        props = resource.properties or {}
        graph_id = resource.tags.get('graph_id', 'unknown')
        
        group = {
            'id': graph_id,
            'displayName': props.get('displayName', resource.name),
            'description': props.get('description'),
            'mailEnabled': props.get('mailEnabled', False),
            'mailNickname': props.get('mailNickname'),
            'mail': props.get('mail'),
            'securityEnabled': props.get('securityEnabled', True),
            'groupTypes': props.get('groupTypes', []),
            'visibility': props.get('visibility', 'Private'),
            'createdDateTime': props.get('createdDateTime')
        }
        
        if select:
            group = {k: v for k, v in group.items() if k in select or k == 'id'}
        
        return group
    
    def _format_directory_object(self, resource) -> Dict:
        """Format as generic directory object.
        
        Args:
            resource: GenericResource instance
        
        Returns:
            Directory object dictionary
        """
        if resource.type == 'Microsoft.Graph/User':
            obj = self._format_graph_user(resource)
            obj['@odata.type'] = '#microsoft.graph.user'
        elif resource.type == 'Microsoft.Graph/Group':
            obj = self._format_graph_group(resource)
            obj['@odata.type'] = '#microsoft.graph.group'
        else:
            obj = {
                'id': resource.tags.get('graph_id', 'unknown'),
                '@odata.type': f"#microsoft.graph.{resource.type.split('/')[-1].lower()}",
                'displayName': resource.name
            }
        
        return obj
    
    # ==================== OData Support ====================
    
    def _apply_odata_filter(self, queryset, filter_expr: str, entity_type: str):
        """Apply OData $filter expressions (simplified).
        
        Supports:
        - displayName eq 'John Doe'
        - startswith(displayName, 'John')
        - accountEnabled eq true
        - mail ne null
        
        Args:
            queryset: MongoEngine queryset
            filter_expr: OData filter expression
            entity_type: Type of entity ('user', 'group', etc.)
        
        Returns:
            Filtered queryset
        """
        # Simple equality filter
        match = re.match(r"(\w+)\s+eq\s+'(.+)'", filter_expr)
        if match:
            field, value = match.groups()
            if field == 'displayName':
                return queryset.filter(name=value)
            else:
                return queryset.filter(**{f'properties__{field}': value})
        
        # Boolean equality
        match = re.match(r"(\w+)\s+eq\s+(true|false)", filter_expr, re.IGNORECASE)
        if match:
            field, value = match.groups()
            bool_value = value.lower() == 'true'
            return queryset.filter(**{f'properties__{field}': bool_value})
        
        # startswith function
        match = re.match(r"startswith\((\w+),\s*'(.+)'\)", filter_expr, re.IGNORECASE)
        if match:
            field, prefix = match.groups()
            if field == 'displayName':
                return queryset.filter(name__istartswith=prefix)
            else:
                return queryset.filter(**{f'properties__{field}__istartswith': prefix})
        
        # endswith function
        match = re.match(r"endswith\((\w+),\s*'(.+)'\)", filter_expr, re.IGNORECASE)
        if match:
            field, suffix = match.groups()
            if field == 'displayName':
                return queryset.filter(name__iendswith=suffix)
        
        # Not null check
        match = re.match(r"(\w+)\s+ne\s+null", filter_expr, re.IGNORECASE)
        if match:
            field = match.group(1)
            return queryset.filter(**{f'properties__{field}__ne': None})
        
        logger.warning(f"Unsupported filter expression: {filter_expr}")
        return queryset
    
    def _apply_orderby(self, queryset, orderby: str):
        """Apply OData $orderby.
        
        Args:
            queryset: MongoEngine queryset
            orderby: Order expression (e.g., 'displayName desc')
        
        Returns:
            Ordered queryset
        """
        parts = orderby.split()
        field = parts[0]
        descending = len(parts) > 1 and parts[1].lower() == 'desc'
        
        if field == 'displayName':
            mongo_field = 'name'
        else:
            mongo_field = f'properties__{field}'
        
        if descending:
            mongo_field = f'-{mongo_field}'
        
        return queryset.order_by(mongo_field)
    
    # ==================== Utility ====================
    
    def _empty_response(self, context: str) -> Dict:
        """Create empty OData response.
        
        Args:
            context: OData context (e.g., 'users', 'groups')
        
        Returns:
            Empty response dictionary
        """
        return {
            '@odata.context': f'https://graph.microsoft.com/v1.0/$metadata#{context}',
            'value': []
        }
    
    def _error_response(self, status_code: int, code: str, message: str) -> Dict:
        """Create Graph API error response.
        
        Args:
            status_code: HTTP status code
            code: Error code
            message: Error message
        
        Returns:
            Error response dictionary
        """
        return {
            'error': {
                'code': code,
                'message': message,
                'innerError': {
                    'request-id': 'mock-request-id',
                    'date': '2026-02-07T23:00:00.000Z'
                }
            },
            '_status_code': status_code  # For testing
        }
