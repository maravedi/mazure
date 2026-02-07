"""Azure Resource Graph query service implementation.

Provides KQL-style query execution against seeded mock state.
Supports basic Resource Graph operations for testing infrastructure queries.
"""

from typing import List, Dict, Any, Optional
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ResourceGraphService:
    """Mock Azure Resource Graph queries using seeded state.
    
    Supports basic KQL operators:
    - Resources | where type =~ 'resourceType'
    - Resources | project name, type, location  
    - Resources | take 10
    - Resources | extend custom = properties.customField
    - Resources | summarize count() by type
    """
    
    def __init__(self, state_manager):
        """Initialize with state manager.
        
        Args:
            state_manager: StateManager instance for accessing resources
        """
        self.state = state_manager
    
    async def query(
        self,
        subscriptions: List[str],
        query: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute KQL-style Resource Graph query against mock state.
        
        Args:
            subscriptions: List of subscription IDs to query
            query: KQL query string
            options: Optional query options (skip, top, etc.)
        
        Returns:
            Resource Graph response with data and metadata
        """
        options = options or {}
        
        try:
            # Parse query type (Resources, ResourceContainers, etc.)
            if query.strip().startswith('Resources'):
                resources = await self._query_resources(subscriptions, query)
            elif query.strip().startswith('ResourceContainers'):
                resources = await self._query_containers(subscriptions, query)
            else:
                raise ValueError(f"Unsupported query table: {query.split()[0]}")
            
            # Apply KQL operators
            resources = await self._apply_query_operators(resources, query)
            
            # Apply pagination from options
            skip = options.get('$skip', options.get('skip', 0))
            top = options.get('$top', options.get('top', 1000))
            
            total_count = len(resources)
            paginated_resources = resources[skip:skip + top]
            
            return {
                'totalRecords': total_count,
                'count': len(paginated_resources),
                'data': paginated_resources,
                'facets': [],
                'resultTruncated': 'false' if total_count == len(paginated_resources) else 'true',
                '$skipToken': str(skip + top) if skip + top < total_count else None
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise
    
    async def _query_resources(
        self,
        subscriptions: List[str],
        query: str
    ) -> List[Dict[str, Any]]:
        """Query Resources table (all ARM resources).
        
        Args:
            subscriptions: Subscription IDs to query
            query: KQL query string
        
        Returns:
            List of resource dictionaries
        """
        # Import here to avoid circular dependencies
        try:
            from mongoengine import Q
            from ..core.state import GenericResource
        except ImportError:
            logger.warning("MongoDB not available, returning empty result")
            return []
        
        all_resources = []
        
        for sub_id in subscriptions:
            try:
                # Get all resource types for subscription, excluding Entra ID pseudo-resources
                resources = GenericResource.objects(
                    Q(subscription_id=sub_id) & ~Q(resource_group='EntraID')
                )
                
                all_resources.extend([r.to_arm_dict() for r in resources])
            except Exception as e:
                logger.warning(f"Failed to query subscription {sub_id}: {str(e)}")
                continue
        
        return all_resources
    
    async def _query_containers(
        self,
        subscriptions: List[str],
        query: str
    ) -> List[Dict[str, Any]]:
        """Query ResourceContainers (subscriptions and resource groups).
        
        Args:
            subscriptions: Subscription IDs
            query: KQL query string
        
        Returns:
            List of container dictionaries
        """
        try:
            from ..core.state import GenericResource
        except ImportError:
            return []
        
        containers = []
        
        for sub_id in subscriptions:
            # Add subscription container
            containers.append({
                'id': f'/subscriptions/{sub_id}',
                'name': sub_id,
                'type': 'microsoft.resources/subscriptions',
                'tenantId': 'mock-tenant-id',
                'subscriptionId': sub_id
            })
            
            # Add resource groups
            try:
                rg_names = GenericResource.objects(
                    subscription_id=sub_id
                ).distinct('resource_group')
                
                for rg_name in rg_names:
                    if rg_name and rg_name != 'EntraID':  # Skip Graph pseudo-RG
                        containers.append({
                            'id': f'/subscriptions/{sub_id}/resourceGroups/{rg_name}',
                            'name': rg_name,
                            'type': 'microsoft.resources/resourcegroups',
                            'location': 'eastus',
                            'subscriptionId': sub_id
                        })
            except Exception as e:
                logger.warning(f"Failed to get resource groups for {sub_id}: {str(e)}")
        
        return containers
    
    async def _apply_query_operators(
        self,
        resources: List[Dict],
        query: str
    ) -> List[Dict]:
        """Apply KQL operators: where, project, take, extend, summarize.
        
        Args:
            resources: List of resource dictionaries
            query: KQL query string
        
        Returns:
            Filtered/transformed resource list
        """
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
            
            elif stage.lower().startswith('order by') or stage.lower().startswith('sort by'):
                resources = self._apply_sort(resources, stage)
        
        return resources
    
    def _filter_where(self, resources: List[Dict], condition: str) -> List[Dict]:
        """Apply WHERE filter (simplified KQL implementation).
        
        Supports:
        - type =~ 'resourceType' (case-insensitive)
        - type == 'resourceType' (case-sensitive)
        - location == 'eastus'
        - name contains 'substring'
        - tags['environment'] == 'prod'
        
        Args:
            resources: List of resources
            condition: WHERE condition string
        
        Returns:
            Filtered resource list
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
            return [r for r in resources if substring.lower() in r.get('name', '').lower()]
        
        # Tag filter
        match = re.search(r"tags\\[['\"](\w+)['\"]\\]\s*==\s*['\"](.+?)['\"]|", condition)
        if match:
            tag_key, tag_value = match.groups()
            return [r for r in resources if r.get('tags', {}).get(tag_key) == tag_value]
        
        # Multiple conditions with 'and'
        if ' and ' in condition.lower():
            parts = re.split(r'\s+and\s+', condition, flags=re.IGNORECASE)
            for part in parts:
                resources = self._filter_where(resources, part.strip())
            return resources
        
        # If no pattern matches, return all (safe default)
        logger.warning(f"Unable to parse WHERE condition: {condition}")
        return resources
    
    def _project_fields(self, resources: List[Dict], fields: List[str]) -> List[Dict]:
        """Project specific fields (SELECT equivalent).
        
        Args:
            resources: List of resources
            fields: List of field names to project
        
        Returns:
            List of projected resources
        """
        projected = []
        
        for r in resources:
            proj = {}
            for field in fields:
                field = field.strip()
                
                # Handle nested properties: properties.field
                if '.' in field:
                    parts = field.split('.')
                    value = r
                    for part in parts:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            value = None
                            break
                    proj[field] = value
                else:
                    proj[field] = r.get(field)
            
            projected.append(proj)
        
        return projected
    
    def _apply_extend(self, resources: List[Dict], expression: str) -> List[Dict]:
        """Add computed columns (EXTEND operator).
        
        Example: extend env = tags['environment']
        
        Args:
            resources: List of resources
            expression: EXTEND expression
        
        Returns:
            Resources with extended fields
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
            
            # Properties extraction
            prop_match = re.search(r"properties\\.([\w.]+)", expr)
            if prop_match:
                prop_path = prop_match.group(1)
                value = r.get('properties', {})
                for part in prop_path.split('.'):
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
                r[new_field] = value
        
        return resources
    
    def _apply_summarize(self, resources: List[Dict], expression: str) -> List[Dict]:
        """Aggregate data (SUMMARIZE operator).
        
        Example: summarize count() by type
        
        Args:
            resources: List of resources
            expression: SUMMARIZE expression
        
        Returns:
            Aggregated results
        """
        # Simple count by field
        match = re.match(r"count\\(\\)\s+by\s+(\w+)", expression)
        if match:
            group_field = match.group(1)
            counts = Counter(r.get(group_field) for r in resources)
            return [
                {group_field: key, 'count': count}
                for key, count in counts.items()
                if key is not None
            ]
        
        # Count without grouping
        if expression.strip().lower() == 'count()':
            return [{'count': len(resources)}]
        
        return resources
    
    def _apply_sort(self, resources: List[Dict], stage: str) -> List[Dict]:
        """Apply sorting (ORDER BY operator).
        
        Args:
            resources: List of resources
            stage: Sort stage string
        
        Returns:
            Sorted resources
        """
        # Extract field and direction
        match = re.search(r"(?:order|sort)\s+by\s+(\w+)(?:\s+(asc|desc))?", stage, re.IGNORECASE)
        if not match:
            return resources
        
        field = match.group(1)
        direction = match.group(2).lower() if match.group(2) else 'asc'
        reverse = (direction == 'desc')
        
        try:
            return sorted(
                resources,
                key=lambda r: r.get(field, ''),
                reverse=reverse
            )
        except Exception as e:
            logger.warning(f"Failed to sort by {field}: {str(e)}")
            return resources
