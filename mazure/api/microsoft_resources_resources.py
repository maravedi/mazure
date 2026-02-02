"""
API Routes for Microsoft.Resources/resources
Generated: 2026-02-01T02:29:44.596021
"""

from flask import Blueprint, request, jsonify
from mazure.core.state import StateManager
from mazure.services.resources.resources import ResourcesService
import asyncio

bp = Blueprint('microsoft_resources_resources', __name__)
state = StateManager()
service = ResourcesService(state)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Operation: Operations_List
# Path: /providers/Microsoft.Resources/operations
@bp.route('/providers/Microsoft.Resources/operations', methods=['GET'])
def operations_list(**kwargs):
    return jsonify({"message": "Generated route for Operations_List", "path_params": kwargs}), 501

# Operation: Providers_Unregister
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/unregister', methods=['POST'])
def providers_unregister(**kwargs):
    return jsonify({"message": "Generated route for Providers_Unregister", "path_params": kwargs}), 501

# Operation: Providers_RegisterAtManagementGroupScope
@bp.route('/providers/Microsoft.Management/managementGroups/<groupId>/providers/<resourceProviderNamespace>/register', methods=['POST'])
def providers_registeratmanagementgroupscope(**kwargs):
    return jsonify({"message": "Generated route for Providers_RegisterAtManagementGroupScope", "path_params": kwargs}), 501

# Operation: Providers_ProviderPermissions
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/providerPermissions', methods=['GET'])
def providers_providerpermissions(**kwargs):
    return jsonify({"message": "Generated route for Providers_ProviderPermissions", "path_params": kwargs}), 501

# Operation: Providers_Register
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/register', methods=['POST'])
def providers_register(**kwargs):
    return jsonify({"message": "Generated route for Providers_Register", "path_params": kwargs}), 501

# Operation: Providers_List
@bp.route('/subscriptions/<subscriptionId>/providers', methods=['GET'])
def providers_list(**kwargs):
    return jsonify({"message": "Generated route for Providers_List", "path_params": kwargs}), 501

# Operation: Providers_ListAtTenantScope
@bp.route('/providers', methods=['GET'])
def providers_listattenantscope(**kwargs):
    return jsonify({"message": "Generated route for Providers_ListAtTenantScope", "path_params": kwargs}), 501

# Operation: Providers_Get
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>', methods=['GET'])
def providers_get(**kwargs):
    return jsonify({"message": "Generated route for Providers_Get", "path_params": kwargs}), 501

# Operation: ProviderResourceTypes_List
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/resourceTypes', methods=['GET'])
def providerresourcetypes_list(**kwargs):
    return jsonify({"message": "Generated route for ProviderResourceTypes_List", "path_params": kwargs}), 501

# Operation: Providers_GetAtTenantScope
@bp.route('/providers/<resourceProviderNamespace>', methods=['GET'])
def providers_getattenantscope(**kwargs):
    return jsonify({"message": "Generated route for Providers_GetAtTenantScope", "path_params": kwargs}), 501

# Operation: Resources_ListByResourceGroup
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/resources', methods=['GET'])
def resources_listbyresourcegroup(**kwargs):
    return jsonify({"message": "Generated route for Resources_ListByResourceGroup", "path_params": kwargs}), 501

# Operation: ResourceGroups_CreateOrUpdate
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>', methods=['PUT'])
def resourcegroups_createorupdate(**kwargs):
    return jsonify({"message": "Generated route for ResourceGroups_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: ResourceGroups_Delete
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>', methods=['DELETE'])
def resourcegroups_delete(**kwargs):
    return jsonify({"message": "Generated route for ResourceGroups_Delete", "path_params": kwargs}), 501

# Operation: ResourceGroups_Get
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>', methods=['GET'])
def resourcegroups_get(**kwargs):
    return jsonify({"message": "Generated route for ResourceGroups_Get", "path_params": kwargs}), 501

# Operation: ResourceGroups_Update
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>', methods=['PATCH'])
def resourcegroups_update(**kwargs):
    return jsonify({"message": "Generated route for ResourceGroups_Update", "path_params": kwargs}), 501

# Operation: ResourceGroups_ExportTemplate
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/exportTemplate', methods=['POST'])
def resourcegroups_exporttemplate(**kwargs):
    return jsonify({"message": "Generated route for ResourceGroups_ExportTemplate", "path_params": kwargs}), 501

# Operation: ResourceGroups_List
@bp.route('/subscriptions/<subscriptionId>/resourcegroups', methods=['GET'])
def resourcegroups_list(**kwargs):
    return jsonify({"message": "Generated route for ResourceGroups_List", "path_params": kwargs}), 501

# Operation: Resources_MoveResources
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<sourceResourceGroupName>/moveResources', methods=['POST'])
def resources_moveresources(**kwargs):
    return jsonify({"message": "Generated route for Resources_MoveResources", "path_params": kwargs}), 501

# Operation: Resources_ValidateMoveResources
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<sourceResourceGroupName>/validateMoveResources', methods=['POST'])
def resources_validatemoveresources(**kwargs):
    return jsonify({"message": "Generated route for Resources_ValidateMoveResources", "path_params": kwargs}), 501

# Operation: Resources_List
@bp.route('/subscriptions/<subscriptionId>/resources', methods=['GET'])
def resources_list(**kwargs):
    return jsonify({"message": "Generated route for Resources_List", "path_params": kwargs}), 501

# Operation: Resources_Delete
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['DELETE'])
def resources_delete(**kwargs):
    try:
        result = run_async(service.resources_delete(
            subscription_id=kwargs.get('subscriptionId'),
            resource_group=kwargs.get('resourceGroupName'),
            resource_name=kwargs.get('resourceName'),
            resource_provider_namespace=kwargs.get('resourceProviderNamespace'),
            resource_type=kwargs.get('resourceType'),
            parent_resource_path=kwargs.get('parentResourcePath'),
            parameters=request.get_json(silent=True) or {},
            **kwargs
        ))
        return jsonify(result)
    except NotImplementedError:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Operation: Resources_Delete (Top Level)
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<resourceType>/<resourceName>', methods=['DELETE'])
def resources_delete_toplevel(**kwargs):
    try:
        result = run_async(service.resources_delete(
            subscription_id=kwargs.get('subscriptionId'),
            resource_group=kwargs.get('resourceGroupName'),
            resource_name=kwargs.get('resourceName'),
            resource_provider_namespace=kwargs.get('resourceProviderNamespace'),
            resource_type=kwargs.get('resourceType'),
            parent_resource_path=None,
            parameters=request.get_json(silent=True) or {},
            **kwargs
        ))
        return jsonify(result)
    except NotImplementedError:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Operation: Resources_CreateOrUpdate
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['PUT'])
def resources_createorupdate(**kwargs):
    try:
        result = run_async(service.resources_createorupdate(
            subscription_id=kwargs.get('subscriptionId'),
            resource_group=kwargs.get('resourceGroupName'),
            resource_name=kwargs.get('resourceName'),
            resource_provider_namespace=kwargs.get('resourceProviderNamespace'),
            resource_type=kwargs.get('resourceType'),
            parent_resource_path=kwargs.get('parentResourcePath'),
            parameters=request.get_json(silent=True) or {},
            **kwargs
        ))
        return jsonify(result)
    except NotImplementedError:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Operation: Resources_CreateOrUpdate (Top Level)
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<resourceType>/<resourceName>', methods=['PUT'])
def resources_createorupdate_toplevel(**kwargs):
    try:
        result = run_async(service.resources_createorupdate(
            subscription_id=kwargs.get('subscriptionId'),
            resource_group=kwargs.get('resourceGroupName'),
            resource_name=kwargs.get('resourceName'),
            resource_provider_namespace=kwargs.get('resourceProviderNamespace'),
            resource_type=kwargs.get('resourceType'),
            parent_resource_path=None,
            parameters=request.get_json(silent=True) or {},
            **kwargs
        ))
        return jsonify(result)
    except NotImplementedError:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Operation: Resources_Update
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['PATCH'])
def resources_update(**kwargs):
    # This is a stub implementation
    return jsonify({"message": "Generated route for Resources_Update", "path_params": kwargs}), 501

# Operation: Resources_Get
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['GET'])
def resources_get(**kwargs):
    try:
        result = run_async(service.resources_get(
            subscription_id=kwargs.get('subscriptionId'),
            resource_group=kwargs.get('resourceGroupName'),
            resource_name=kwargs.get('resourceName'),
            resource_provider_namespace=kwargs.get('resourceProviderNamespace'),
            resource_type=kwargs.get('resourceType'),
            parent_resource_path=kwargs.get('parentResourcePath'),
            parameters=request.get_json(silent=True) or {},
            **kwargs
        ))
        return jsonify(result)
    except NotImplementedError:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Operation: Resources_Get (Top Level)
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<resourceType>/<resourceName>', methods=['GET'])
def resources_get_toplevel(**kwargs):
    try:
        result = run_async(service.resources_get(
            subscription_id=kwargs.get('subscriptionId'),
            resource_group=kwargs.get('resourceGroupName'),
            resource_name=kwargs.get('resourceName'),
            resource_provider_namespace=kwargs.get('resourceProviderNamespace'),
            resource_type=kwargs.get('resourceType'),
            parent_resource_path=None,
            parameters=request.get_json(silent=True) or {},
            **kwargs
        ))
        return jsonify(result)
    except NotImplementedError:
        return jsonify({"error": "Not implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Operation: Resources_DeleteById
@bp.route('/<resourceId>', methods=['DELETE'])
def resources_deletebyid(**kwargs):
    return jsonify({"message": "Generated route for Resources_DeleteById", "path_params": kwargs}), 501

# Operation: Resources_CreateOrUpdateById
@bp.route('/<resourceId>', methods=['PUT'])
def resources_createorupdatebyid(**kwargs):
    return jsonify({"message": "Generated route for Resources_CreateOrUpdateById", "path_params": kwargs}), 501

# Operation: Resources_UpdateById
@bp.route('/<resourceId>', methods=['PATCH'])
def resources_updatebyid(**kwargs):
    return jsonify({"message": "Generated route for Resources_UpdateById", "path_params": kwargs}), 501

# Operation: Resources_GetById
@bp.route('/<resourceId>', methods=['GET'])
def resources_getbyid(**kwargs):
    return jsonify({"message": "Generated route for Resources_GetById", "path_params": kwargs}), 501

# Operation: Tags_DeleteValue
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>/tagValues/<tagValue>', methods=['DELETE'])
def tags_deletevalue(**kwargs):
    return jsonify({"message": "Generated route for Tags_DeleteValue", "path_params": kwargs}), 501

# Operation: Tags_CreateOrUpdateValue
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>/tagValues/<tagValue>', methods=['PUT'])
def tags_createorupdatevalue(**kwargs):
    return jsonify({"message": "Generated route for Tags_CreateOrUpdateValue", "path_params": kwargs}), 501

# Operation: Tags_CreateOrUpdate
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>', methods=['PUT'])
def tags_createorupdate(**kwargs):
    return jsonify({"message": "Generated route for Tags_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: Tags_Delete
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>', methods=['DELETE'])
def tags_delete(**kwargs):
    return jsonify({"message": "Generated route for Tags_Delete", "path_params": kwargs}), 501

# Operation: Tags_List
@bp.route('/subscriptions/<subscriptionId>/tagNames', methods=['GET'])
def tags_list(**kwargs):
    return jsonify({"message": "Generated route for Tags_List", "path_params": kwargs}), 501

# Operation: Tags_CreateOrUpdateAtScope
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['PUT'])
def tags_createorupdateatscope(**kwargs):
    return jsonify({"message": "Generated route for Tags_CreateOrUpdateAtScope", "path_params": kwargs}), 501

# Operation: Tags_UpdateAtScope
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['PATCH'])
def tags_updateatscope(**kwargs):
    return jsonify({"message": "Generated route for Tags_UpdateAtScope", "path_params": kwargs}), 501

# Operation: Tags_GetAtScope
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['GET'])
def tags_getatscope(**kwargs):
    return jsonify({"message": "Generated route for Tags_GetAtScope", "path_params": kwargs}), 501

# Operation: Tags_DeleteAtScope
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['DELETE'])
def tags_deleteatscope(**kwargs):
    return jsonify({"message": "Generated route for Tags_DeleteAtScope", "path_params": kwargs}), 501
