"""
Microsoft.Resources/resources Service Implementation
Auto-generated from Azure REST API specifications
Generated: 2026-02-01T02:29:44.566770
API Version: 2025-04-01
"""

from typing import Optional, Dict, Any, List
from mazure.core.state import StateManager
# from mazure.schemas.microsoft_resources import *

class ResourcesService:
    """Implements Microsoft.Resources/resources API"""

    RESOURCE_TYPE = "Microsoft.Resources/resources"
    API_VERSIONS = ["2025-04-01"]

    def __init__(self, state: StateManager):
        self.state = state

    
    async def create_or_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        parameters: Dict[str, Any],
        api_version: str = "2025-04-01"
    ) -> Dict[str, Any]:
        """Creates or updates the entire set of tags on a resource or subscription."""

        # Validate required fields
        # if 'location' not in parameters:
        #    raise ValueError("location is required")

        # Check if exists
        existing = await self.state.get_resource(
            subscription_id, resource_group, self.RESOURCE_TYPE, resource_name
        )

        if existing:
            # Update
            resource = await self.state.update_resource(
                existing.resource_id,
                properties=parameters.get('properties'),
                tags=parameters.get('tags')
            )
            return resource.to_arm_dict()
        else:
            # Create
            resource = await self.state.create_resource(
                resource_type=self.RESOURCE_TYPE,
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=resource_name,
                properties=parameters.get('properties', {}),
                location=parameters.get('location', 'eastus'),
                tags=parameters.get('tags'),
                api_version=api_version
            )
            return resource.to_arm_dict()
    

    
    async def get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get resource details"""

        resource = await self.state.get_resource(
            subscription_id, resource_group, self.RESOURCE_TYPE, resource_name
        )

        return resource.to_arm_dict() if resource else None
    

    
    async def list(
        self,
        subscription_id: str,
        resource_group: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Gets the entire set of tags on a resource or subscription."""

        resources = await self.state.list_resources(
            subscription_id, resource_group, self.RESOURCE_TYPE
        )

        return [r.to_arm_dict() for r in resources]
    

    
    async def delete(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str
    ) -> bool:
        """Deletes the entire set of tags on a resource or subscription."""

        return await self.state.delete_resource(
            subscription_id, resource_group, self.RESOURCE_TYPE, resource_name
        )
    

    
    
    async def operations_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Lists all of the available Microsoft.Resources REST API operations."""

        # TODO: Implement Operations_List
        raise NotImplementedError("Operations_List not yet implemented")
    
    
    
    async def providers_unregister(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Unregisters a subscription from a resource provider."""

        # TODO: Implement Providers_Unregister
        raise NotImplementedError("Providers_Unregister not yet implemented")
    
    
    
    async def providers_registeratmanagementgroupscope(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Registers a management group with a resource provider. Use this operation to register a resource provider with resource types that can be deployed at the management group scope. It does not recursively register subscriptions within the management group. Instead, you must register subscriptions individually."""

        # TODO: Implement Providers_RegisterAtManagementGroupScope
        raise NotImplementedError("Providers_RegisterAtManagementGroupScope not yet implemented")
    
    
    
    async def providers_providerpermissions(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get the provider permissions."""

        # TODO: Implement Providers_ProviderPermissions
        raise NotImplementedError("Providers_ProviderPermissions not yet implemented")
    
    
    
    async def providers_register(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Registers a subscription with a resource provider."""

        # TODO: Implement Providers_Register
        raise NotImplementedError("Providers_Register not yet implemented")
    
    
    
    async def providers_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets all resource providers for a subscription."""

        # TODO: Implement Providers_List
        raise NotImplementedError("Providers_List not yet implemented")
    
    
    
    async def providers_listattenantscope(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets all resource providers for the tenant."""

        # TODO: Implement Providers_ListAtTenantScope
        raise NotImplementedError("Providers_ListAtTenantScope not yet implemented")
    
    
    
    async def providers_get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets the specified resource provider."""

        # TODO: Implement Providers_Get
        raise NotImplementedError("Providers_Get not yet implemented")
    
    
    
    async def providerresourcetypes_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """List the resource types for a specified resource provider."""

        # TODO: Implement ProviderResourceTypes_List
        raise NotImplementedError("ProviderResourceTypes_List not yet implemented")
    
    
    
    async def providers_getattenantscope(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets the specified resource provider at the tenant level."""

        # TODO: Implement Providers_GetAtTenantScope
        raise NotImplementedError("Providers_GetAtTenantScope not yet implemented")
    
    
    
    async def resources_listbyresourcegroup(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get all the resources for a resource group."""

        # TODO: Implement Resources_ListByResourceGroup
        raise NotImplementedError("Resources_ListByResourceGroup not yet implemented")
    
    
    
    async def resourcegroups_createorupdate(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Creates or updates a resource group."""

        # TODO: Implement ResourceGroups_CreateOrUpdate
        raise NotImplementedError("ResourceGroups_CreateOrUpdate not yet implemented")
    
    
    
    async def resourcegroups_delete(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Deletes a resource group."""

        # TODO: Implement ResourceGroups_Delete
        raise NotImplementedError("ResourceGroups_Delete not yet implemented")
    
    
    
    async def resourcegroups_get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets a resource group."""

        # TODO: Implement ResourceGroups_Get
        raise NotImplementedError("ResourceGroups_Get not yet implemented")
    
    
    
    async def resourcegroups_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Updates a resource group."""

        # TODO: Implement ResourceGroups_Update
        raise NotImplementedError("ResourceGroups_Update not yet implemented")
    
    
    
    async def resourcegroups_exporttemplate(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Captures the specified resource group as a template."""

        # TODO: Implement ResourceGroups_ExportTemplate
        raise NotImplementedError("ResourceGroups_ExportTemplate not yet implemented")
    
    
    
    async def resourcegroups_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets all the resource groups for a subscription."""

        # TODO: Implement ResourceGroups_List
        raise NotImplementedError("ResourceGroups_List not yet implemented")
    
    
    
    async def resources_moveresources(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Moves resources from one resource group to another resource group."""

        # TODO: Implement Resources_MoveResources
        raise NotImplementedError("Resources_MoveResources not yet implemented")
    
    
    
    async def resources_validatemoveresources(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Validates whether resources can be moved from one resource group to another resource group."""

        # TODO: Implement Resources_ValidateMoveResources
        raise NotImplementedError("Resources_ValidateMoveResources not yet implemented")
    
    
    
    async def resources_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get all the resources in a subscription."""

        # TODO: Implement Resources_List
        raise NotImplementedError("Resources_List not yet implemented")
    
    
    
    async def resources_delete(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Deletes a resource."""

        # TODO: Implement Resources_Delete
        raise NotImplementedError("Resources_Delete not yet implemented")
    
    
    
    async def resources_createorupdate(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Creates a resource."""

        # TODO: Implement Resources_CreateOrUpdate
        raise NotImplementedError("Resources_CreateOrUpdate not yet implemented")
    
    
    
    async def resources_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Updates a resource."""

        # TODO: Implement Resources_Update
        raise NotImplementedError("Resources_Update not yet implemented")
    
    
    
    async def resources_get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets a resource."""

        # TODO: Implement Resources_Get
        raise NotImplementedError("Resources_Get not yet implemented")
    
    
    
    async def resources_deletebyid(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Deletes a resource by ID."""

        # TODO: Implement Resources_DeleteById
        raise NotImplementedError("Resources_DeleteById not yet implemented")
    
    
    
    async def resources_createorupdatebyid(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a resource by ID."""

        # TODO: Implement Resources_CreateOrUpdateById
        raise NotImplementedError("Resources_CreateOrUpdateById not yet implemented")
    
    
    
    async def resources_updatebyid(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Updates a resource by ID."""

        # TODO: Implement Resources_UpdateById
        raise NotImplementedError("Resources_UpdateById not yet implemented")
    
    
    
    async def resources_getbyid(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets a resource by ID."""

        # TODO: Implement Resources_GetById
        raise NotImplementedError("Resources_GetById not yet implemented")
    
    
    
    async def tags_deletevalue(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Deletes a predefined tag value for a predefined tag name."""

        # TODO: Implement Tags_DeleteValue
        raise NotImplementedError("Tags_DeleteValue not yet implemented")
    
    
    
    async def tags_createorupdatevalue(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Creates a predefined value for a predefined tag name."""

        # TODO: Implement Tags_CreateOrUpdateValue
        raise NotImplementedError("Tags_CreateOrUpdateValue not yet implemented")
    
    
    
    async def tags_createorupdate(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Creates a predefined tag name."""

        # TODO: Implement Tags_CreateOrUpdate
        raise NotImplementedError("Tags_CreateOrUpdate not yet implemented")
    
    
    
    async def tags_delete(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Deletes a predefined tag name."""

        # TODO: Implement Tags_Delete
        raise NotImplementedError("Tags_Delete not yet implemented")
    
    
    
    async def tags_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets a summary of tag usage under the subscription."""

        # TODO: Implement Tags_List
        raise NotImplementedError("Tags_List not yet implemented")
    
    
    
    
    
    async def tags_updateatscope(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Selectively updates the set of tags on a resource or subscription."""

        # TODO: Implement Tags_UpdateAtScope
        raise NotImplementedError("Tags_UpdateAtScope not yet implemented")
    
    
    
    
    
    