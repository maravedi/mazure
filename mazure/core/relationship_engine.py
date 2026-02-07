"""Relationship engine for managing resource dependencies and cascading operations.

Handles:
- Cascading deletes with dry-run support
- Dependency validation on resource creation
- Impact analysis and dependency trees
- Resource graph traversal
"""

from typing import List, Dict, Any, Set, Optional
import logging

logger = logging.getLogger(__name__)


class RelationshipEngine:
    """Handle cascading operations based on resource relationships.
    
    Uses relationship data from discovery to implement:
    - Cascading deletes
    - Dependency validation
    - Impact analysis
    - Resource group operations
    """
    
    def __init__(self, state_manager):
        """Initialize with state manager.
        
        Args:
            state_manager: StateManager instance
        """
        self.state = state_manager
    
    async def delete_with_dependents(
        self,
        resource_id: str,
        cascade: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Delete resource and optionally cascade to dependents.
        
        Args:
            resource_id: ARM resource ID
            cascade: If True, delete dependent resources
            dry_run: If True, return what would be deleted without deleting
        
        Returns:
            Dict with deleted resource IDs and dependency info
        """
        try:
            from .relationships import ResourceRelationship
            from mongoengine import Q
        except ImportError:
            return {
                'error': 'Relationship tracking not available',
                'deleted': [],
                'count': 0
            }
        
        # Find all relationships where this resource is the source
        outbound_rels = ResourceRelationship.objects(source_id=resource_id)
        
        # Find all relationships where this resource is the target (dependents)
        inbound_rels = ResourceRelationship.objects(target_id=resource_id)
        
        deleted_ids = []
        blocked_by = []
        warnings = []
        
        # Check for blocking dependencies
        for rel in inbound_rels:
            if rel.relation_type in ['depends_on', 'required_by', 'child_of']:
                if not cascade:
                    blocked_by.append({
                        'resource_id': rel.source_id,
                        'relation_type': rel.relation_type
                    })
        
        if blocked_by and not cascade:
            return {
                'error': 'Resource has dependents',
                'blocked_by': blocked_by,
                'message': (
                    f"Cannot delete {resource_id}: has {len(blocked_by)} dependent resources. "
                    f"Use cascade=True to delete dependents."
                ),
                'deleted': [],
                'count': 0
            }
        
        # Build deletion plan
        to_delete = await self._build_deletion_tree(
            resource_id,
            cascade,
            visited=set()
        )
        
        if dry_run:
            return {
                'dry_run': True,
                'would_delete': to_delete,
                'count': len(to_delete),
                'warnings': warnings,
                'cascade': cascade
            }
        
        # Execute deletions in reverse dependency order
        for rid in reversed(to_delete):
            try:
                success = await self._delete_resource_by_id(rid)
                if success:
                    deleted_ids.append(rid)
                    
                    # Delete relationships involving this resource
                    ResourceRelationship.objects(
                        Q(source_id=rid) | Q(target_id=rid)
                    ).delete()
            except Exception as e:
                logger.error(f"Failed to delete {rid}: {str(e)}")
                warnings.append(f"Failed to delete {rid}: {str(e)}")
        
        return {
            'deleted': deleted_ids,
            'count': len(deleted_ids),
            'cascade': cascade,
            'warnings': warnings
        }
    
    async def _build_deletion_tree(
        self,
        resource_id: str,
        cascade: bool,
        visited: Set[str]
    ) -> List[str]:
        """Build ordered list of resources to delete.
        
        Uses depth-first traversal to build deletion order.
        
        Args:
            resource_id: Resource to delete
            cascade: Whether to include dependents
            visited: Set of already visited resources
        
        Returns:
            List of resource IDs in deletion order
        """
        if resource_id in visited:
            return []
        
        visited.add(resource_id)
        to_delete = []
        
        if cascade:
            try:
                from .relationships import ResourceRelationship
                
                # Find resources contained by or dependent on this one
                child_rels = ResourceRelationship.objects(
                    source_id=resource_id,
                    relation_type__in=['contains', 'parent_of']
                )
                
                dependent_rels = ResourceRelationship.objects(
                    target_id=resource_id,
                    relation_type__in=['depends_on', 'child_of']
                )
                
                # Recursively add children
                for rel in child_rels:
                    child_tree = await self._build_deletion_tree(
                        rel.target_id,
                        cascade=True,
                        visited=visited
                    )
                    to_delete.extend(child_tree)
                
                # Recursively add dependents
                for rel in dependent_rels:
                    dep_tree = await self._build_deletion_tree(
                        rel.source_id,
                        cascade=True,
                        visited=visited
                    )
                    to_delete.extend(dep_tree)
                    
            except Exception as e:
                logger.warning(f"Failed to build deletion tree: {str(e)}")
        
        # Add this resource last (delete children first)
        to_delete.append(resource_id)
        
        return to_delete
    
    async def _delete_resource_by_id(self, resource_id: str) -> bool:
        """Delete resource by ARM resource ID.
        
        Args:
            resource_id: ARM resource ID
        
        Returns:
            True if deleted successfully
        """
        try:
            from .state import GenericResource
            
            resource = GenericResource.objects(resource_id=resource_id).first()
            if resource:
                resource.delete()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete resource {resource_id}: {str(e)}")
            return False
    
    async def validate_create(
        self,
        resource_type: str,
        properties: Dict[str, Any],
        subscription_id: str = None,
        resource_group: str = None
    ) -> Dict[str, Any]:
        """Validate resource creation against dependencies.
        
        Checks if required resources exist (e.g., subnet for VM NIC).
        
        Args:
            resource_type: Azure resource type
            properties: Resource properties
            subscription_id: Subscription ID
            resource_group: Resource group name
        
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        # Resource-type-specific dependency checks
        if resource_type == 'Microsoft.Compute/virtualMachines':
            errors.extend(await self._validate_vm_dependencies(properties))
        
        elif resource_type == 'Microsoft.Network/networkInterfaces':
            errors.extend(await self._validate_nic_dependencies(properties))
        
        elif resource_type == 'Microsoft.Network/publicIPAddresses':
            # Public IPs have no hard dependencies
            pass
        
        elif resource_type == 'Microsoft.Storage/storageAccounts':
            # Storage accounts have no hard dependencies
            pass
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def _validate_vm_dependencies(self, properties: Dict[str, Any]) -> List[str]:
        """Validate VM dependencies.
        
        Args:
            properties: VM properties
        
        Returns:
            List of error messages
        """
        errors = []
        
        # Check network interface references
        network_profile = properties.get('networkProfile', {})
        nic_refs = network_profile.get('networkInterfaces', [])
        
        for nic_ref in nic_refs:
            nic_id = nic_ref.get('id')
            if nic_id:
                exists = await self._resource_exists(nic_id)
                if not exists:
                    errors.append(f"Referenced network interface not found: {nic_id}")
        
        # Check OS disk reference (if managed disk)
        storage_profile = properties.get('storageProfile', {})
        os_disk = storage_profile.get('osDisk', {})
        managed_disk = os_disk.get('managedDisk', {})
        disk_id = managed_disk.get('id')
        
        if disk_id:
            exists = await self._resource_exists(disk_id)
            if not exists:
                errors.append(f"Referenced OS disk not found: {disk_id}")
        
        return errors
    
    async def _validate_nic_dependencies(self, properties: Dict[str, Any]) -> List[str]:
        """Validate NIC dependencies.
        
        Args:
            properties: NIC properties
        
        Returns:
            List of error messages
        """
        errors = []
        
        # Check subnet reference
        ip_configs = properties.get('ipConfigurations', [])
        for config in ip_configs:
            subnet_ref = config.get('subnet', {}).get('id')
            if subnet_ref:
                exists = await self._resource_exists(subnet_ref)
                if not exists:
                    errors.append(f"Referenced subnet not found: {subnet_ref}")
            
            # Check public IP reference
            public_ip_ref = config.get('publicIPAddress', {}).get('id')
            if public_ip_ref:
                exists = await self._resource_exists(public_ip_ref)
                if not exists:
                    errors.append(f"Referenced public IP not found: {public_ip_ref}")
        
        # Check network security group
        nsg_ref = properties.get('networkSecurityGroup', {}).get('id')
        if nsg_ref:
            exists = await self._resource_exists(nsg_ref)
            if not exists:
                errors.append(f"Referenced network security group not found: {nsg_ref}")
        
        return errors
    
    async def _resource_exists(self, resource_id: str) -> bool:
        """Check if resource exists in mock state.
        
        Args:
            resource_id: ARM resource ID
        
        Returns:
            True if resource exists
        """
        try:
            from .state import GenericResource
            resource = GenericResource.objects(resource_id=resource_id).first()
            return resource is not None
        except Exception:
            return False
    
    async def get_resource_dependencies(
        self,
        resource_id: str,
        depth: int = 1,
        include_dependents: bool = True
    ) -> Dict[str, Any]:
        """Get dependency tree for a resource.
        
        Args:
            resource_id: ARM resource ID
            depth: How many levels deep to traverse (0 = infinite)
            include_dependents: Include resources that depend on this one
        
        Returns:
            Dependency tree with inbound and outbound relationships
        """
        try:
            from .relationships import ResourceRelationship
        except ImportError:
            return {
                'resource_id': resource_id,
                'error': 'Relationship tracking not available'
            }
        
        # Get outbound relationships (resources this depends on)
        outbound = ResourceRelationship.objects(source_id=resource_id)
        
        # Get inbound relationships (resources that depend on this)
        inbound = ResourceRelationship.objects(target_id=resource_id)
        
        tree = {
            'resource_id': resource_id,
            'depends_on': [],
            'depended_by': []
        }
        
        # Build depends_on tree
        for rel in outbound:
            dep = {
                'resource_id': rel.target_id,
                'relation_type': rel.relation_type,
                'weight': rel.weight
            }
            
            # Recursive traversal
            if depth != 1:
                next_depth = depth - 1 if depth > 0 else 0
                dep['dependencies'] = await self.get_resource_dependencies(
                    rel.target_id,
                    depth=next_depth,
                    include_dependents=False
                )
            
            tree['depends_on'].append(dep)
        
        # Build depended_by tree
        if include_dependents:
            for rel in inbound:
                dep = {
                    'resource_id': rel.source_id,
                    'relation_type': rel.relation_type,
                    'weight': rel.weight
                }
                
                tree['depended_by'].append(dep)
        
        return tree
    
    async def analyze_impact(
        self,
        resource_id: str,
        operation: str = 'delete'
    ) -> Dict[str, Any]:
        """Analyze impact of an operation on a resource.
        
        Args:
            resource_id: ARM resource ID
            operation: Operation to analyze (delete, modify, etc.)
        
        Returns:
            Impact analysis with affected resources
        """
        if operation == 'delete':
            # Use dry-run delete to see impact
            return await self.delete_with_dependents(
                resource_id,
                cascade=True,
                dry_run=True
            )
        
        elif operation == 'modify':
            # Get all dependents
            deps = await self.get_resource_dependencies(
                resource_id,
                depth=0,
                include_dependents=True
            )
            
            return {
                'operation': 'modify',
                'resource_id': resource_id,
                'potentially_affected': deps['depended_by'],
                'message': f"{len(deps['depended_by'])} resources may be affected by modification"
            }
        
        else:
            return {
                'error': f"Unsupported operation: {operation}"
            }
