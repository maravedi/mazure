
"""
Pydantic schemas for Microsoft.Resources
Generated: 2026-02-01T02:29:44.581266
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel



class GenericResourceFilter(BaseModel):
    """Resource filter."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceGroupFilter(BaseModel):
    """Resource group filter."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class CloudError(BaseModel):
    """An error response for a resource management request."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ApiProfile(BaseModel):
    """ApiProfile"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class AliasPathMetadata(BaseModel):
    """AliasPathMetadata"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class AliasPath(BaseModel):
    """The type of the paths for alias."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class AliasPattern(BaseModel):
    """The type of the pattern for an alias path."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Alias(BaseModel):
    """The alias type. """
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderExtendedLocation(BaseModel):
    """The provider extended location. """
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderResourceType(BaseModel):
    """Resource type managed by the resource provider."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Provider(BaseModel):
    """Resource provider information."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderListResult(BaseModel):
    """List of resource providers."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderResourceTypeListResult(BaseModel):
    """List of resource types of a resource provider."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class GenericResource(BaseModel):
    """Resource information."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ExtendedLocation(BaseModel):
    """Resource extended location."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class GenericResourceExpanded(BaseModel):
    """Resource information."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Plan(BaseModel):
    """Plan for the resource."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Sku(BaseModel):
    """SKU for the resource."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Identity(BaseModel):
    """Identity for the resource."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceListResult(BaseModel):
    """List of resource groups."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceGroup(BaseModel):
    """Resource group information."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceGroupPatchable(BaseModel):
    """Resource group information."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceGroupProperties(BaseModel):
    """The resource group properties."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceGroupListResult(BaseModel):
    """List of resource groups."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourcesMoveInfo(BaseModel):
    """Parameters of move resources."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ExportTemplateRequest(BaseModel):
    """Export resource group template request parameters."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class TagCount(BaseModel):
    """Tag count."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class TagValue(BaseModel):
    """Tag information."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class TagDetails(BaseModel):
    """Tag details."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class TagsListResult(BaseModel):
    """List of subscription tags."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceProviderOperationDisplayProperties(BaseModel):
    """Resource provider operation's display properties."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Resource(BaseModel):
    """Specified resource."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class SubResource(BaseModel):
    """Sub-resource."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ResourceGroupExportResult(BaseModel):
    """Resource group export result."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Operation(BaseModel):
    """Microsoft.Resources operation"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class OperationListResult(BaseModel):
    """Result of the request to list Microsoft.Resources operations. It contains a list of operations and a URL link to get the next set of results."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Tags(BaseModel):
    """A dictionary of name and value pairs."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class TagsPatchResource(BaseModel):
    """Wrapper resource for tags patch API request only."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class TagsResource(BaseModel):
    """Wrapper resource for tags API requests and responses."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class Permission(BaseModel):
    """Role definition permissions."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class RoleDefinition(BaseModel):
    """Role definition properties."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderPermission(BaseModel):
    """The provider permission"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderPermissionListResult(BaseModel):
    """List of provider permissions."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderConsentDefinition(BaseModel):
    """The provider consent."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ProviderRegistrationRequest(BaseModel):
    """The provider registration definition."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class ZoneMapping(BaseModel):
    """ZoneMapping"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types

