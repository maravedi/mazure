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
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.operations_list(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Operations_List", "path_params": kwargs}), 501

# Operation: Providers_Unregister
# Path: /subscriptions/{subscriptionId}/providers/{resourceProviderNamespace}/unregister
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/unregister', methods=['POST'])
def providers_unregister(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_unregister(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_Unregister", "path_params": kwargs}), 501

# Operation: Providers_RegisterAtManagementGroupScope
# Path: /providers/Microsoft.Management/managementGroups/{groupId}/providers/{resourceProviderNamespace}/register
@bp.route('/providers/Microsoft.Management/managementGroups/<groupId>/providers/<resourceProviderNamespace>/register', methods=['POST'])
def providers_registeratmanagementgroupscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_registeratmanagementgroupscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_RegisterAtManagementGroupScope", "path_params": kwargs}), 501

# Operation: Providers_ProviderPermissions
# Path: /subscriptions/{subscriptionId}/providers/{resourceProviderNamespace}/providerPermissions
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/providerPermissions', methods=['GET'])
def providers_providerpermissions(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_providerpermissions(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_ProviderPermissions", "path_params": kwargs}), 501

# Operation: Providers_Register
# Path: /subscriptions/{subscriptionId}/providers/{resourceProviderNamespace}/register
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/register', methods=['POST'])
def providers_register(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_register(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_Register", "path_params": kwargs}), 501

# Operation: Providers_List
# Path: /subscriptions/{subscriptionId}/providers
@bp.route('/subscriptions/<subscriptionId>/providers', methods=['GET'])
def providers_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_list(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_List", "path_params": kwargs}), 501

# Operation: Providers_ListAtTenantScope
# Path: /providers
@bp.route('/providers', methods=['GET'])
def providers_listattenantscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_listattenantscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_ListAtTenantScope", "path_params": kwargs}), 501

# Operation: Providers_Get
# Path: /subscriptions/{subscriptionId}/providers/{resourceProviderNamespace}
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>', methods=['GET'])
def providers_get(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_get(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_Get", "path_params": kwargs}), 501

# Operation: ProviderResourceTypes_List
# Path: /subscriptions/{subscriptionId}/providers/{resourceProviderNamespace}/resourceTypes
@bp.route('/subscriptions/<subscriptionId>/providers/<resourceProviderNamespace>/resourceTypes', methods=['GET'])
def providerresourcetypes_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providerresourcetypes_list(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ProviderResourceTypes_List", "path_params": kwargs}), 501

# Operation: Providers_GetAtTenantScope
# Path: /providers/{resourceProviderNamespace}
@bp.route('/providers/<resourceProviderNamespace>', methods=['GET'])
def providers_getattenantscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.providers_getattenantscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Providers_GetAtTenantScope", "path_params": kwargs}), 501

# Operation: Resources_ListByResourceGroup
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/resources
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/resources', methods=['GET'])
def resources_listbyresourcegroup(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_listbyresourcegroup(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_ListByResourceGroup", "path_params": kwargs}), 501

# Operation: ResourceGroups_CreateOrUpdate
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>', methods=['PUT'])
def resourcegroups_createorupdate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resourcegroups_createorupdate(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ResourceGroups_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: ResourceGroups_Delete
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>', methods=['DELETE'])
def resourcegroups_delete(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resourcegroups_delete(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ResourceGroups_Delete", "path_params": kwargs}), 501

# Operation: ResourceGroups_Get
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>', methods=['GET'])
def resourcegroups_get(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resourcegroups_get(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ResourceGroups_Get", "path_params": kwargs}), 501

# Operation: ResourceGroups_Update
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>', methods=['PATCH'])
def resourcegroups_update(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resourcegroups_update(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ResourceGroups_Update", "path_params": kwargs}), 501

# Operation: ResourceGroups_ExportTemplate
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/exportTemplate
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>/exportTemplate', methods=['POST'])
def resourcegroups_exporttemplate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resourcegroups_exporttemplate(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ResourceGroups_ExportTemplate", "path_params": kwargs}), 501

# Operation: ResourceGroups_List
# Path: /subscriptions/{subscriptionId}/resourcegroups
@bp.route('/subscriptions/<subscriptionId>/resourcegroups', methods=['GET'])
def resourcegroups_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resourcegroups_list(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for ResourceGroups_List", "path_params": kwargs}), 501

# Operation: Resources_MoveResources
# Path: /subscriptions/{subscriptionId}/resourceGroups/{sourceResourceGroupName}/moveResources
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<sourceResourceGroupName>/moveResources', methods=['POST'])
def resources_moveresources(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_moveresources(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_MoveResources", "path_params": kwargs}), 501

# Operation: Resources_ValidateMoveResources
# Path: /subscriptions/{subscriptionId}/resourceGroups/{sourceResourceGroupName}/validateMoveResources
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<sourceResourceGroupName>/validateMoveResources', methods=['POST'])
def resources_validatemoveresources(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_validatemoveresources(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_ValidateMoveResources", "path_params": kwargs}), 501

# Operation: Resources_List
# Path: /subscriptions/{subscriptionId}/resources
@bp.route('/subscriptions/<subscriptionId>/resources', methods=['GET'])
def resources_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_list(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_List", "path_params": kwargs}), 501

# Operation: Resources_Delete
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{parentResourcePath}/{resourceType}/{resourceName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['DELETE'])
def resources_delete(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_delete(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_Delete", "path_params": kwargs}), 501

# Operation: Resources_CreateOrUpdate
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{parentResourcePath}/{resourceType}/{resourceName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['PUT'])
def resources_createorupdate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_createorupdate(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: Resources_Update
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{parentResourcePath}/{resourceType}/{resourceName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['PATCH'])
def resources_update(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_update(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_Update", "path_params": kwargs}), 501

# Operation: Resources_Get
# Path: /subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{parentResourcePath}/{resourceType}/{resourceName}
@bp.route('/subscriptions/<subscriptionId>/resourcegroups/<resourceGroupName>/providers/<resourceProviderNamespace>/<parentResourcePath>/<resourceType>/<resourceName>', methods=['GET'])
def resources_get(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_get(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_Get", "path_params": kwargs}), 501

# Operation: Resources_DeleteById
# Path: /{resourceId}
@bp.route('/<resourceId>', methods=['DELETE'])
def resources_deletebyid(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_deletebyid(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_DeleteById", "path_params": kwargs}), 501

# Operation: Resources_CreateOrUpdateById
# Path: /{resourceId}
@bp.route('/<resourceId>', methods=['PUT'])
def resources_createorupdatebyid(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_createorupdatebyid(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_CreateOrUpdateById", "path_params": kwargs}), 501

# Operation: Resources_UpdateById
# Path: /{resourceId}
@bp.route('/<resourceId>', methods=['PATCH'])
def resources_updatebyid(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_updatebyid(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_UpdateById", "path_params": kwargs}), 501

# Operation: Resources_GetById
# Path: /{resourceId}
@bp.route('/<resourceId>', methods=['GET'])
def resources_getbyid(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.resources_getbyid(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Resources_GetById", "path_params": kwargs}), 501

# Operation: Tags_DeleteValue
# Path: /subscriptions/{subscriptionId}/tagNames/{tagName}/tagValues/{tagValue}
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>/tagValues/<tagValue>', methods=['DELETE'])
def tags_deletevalue(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_deletevalue(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_DeleteValue", "path_params": kwargs}), 501

# Operation: Tags_CreateOrUpdateValue
# Path: /subscriptions/{subscriptionId}/tagNames/{tagName}/tagValues/{tagValue}
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>/tagValues/<tagValue>', methods=['PUT'])
def tags_createorupdatevalue(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_createorupdatevalue(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_CreateOrUpdateValue", "path_params": kwargs}), 501

# Operation: Tags_CreateOrUpdate
# Path: /subscriptions/{subscriptionId}/tagNames/{tagName}
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>', methods=['PUT'])
def tags_createorupdate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_createorupdate(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: Tags_Delete
# Path: /subscriptions/{subscriptionId}/tagNames/{tagName}
@bp.route('/subscriptions/<subscriptionId>/tagNames/<tagName>', methods=['DELETE'])
def tags_delete(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_delete(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_Delete", "path_params": kwargs}), 501

# Operation: Tags_List
# Path: /subscriptions/{subscriptionId}/tagNames
@bp.route('/subscriptions/<subscriptionId>/tagNames', methods=['GET'])
def tags_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_list(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_List", "path_params": kwargs}), 501

# Operation: Tags_CreateOrUpdateAtScope
# Path: /{scope}/providers/Microsoft.Resources/tags/default
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['PUT'])
def tags_createorupdateatscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_createorupdateatscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_CreateOrUpdateAtScope", "path_params": kwargs}), 501

# Operation: Tags_UpdateAtScope
# Path: /{scope}/providers/Microsoft.Resources/tags/default
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['PATCH'])
def tags_updateatscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_updateatscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_UpdateAtScope", "path_params": kwargs}), 501

# Operation: Tags_GetAtScope
# Path: /{scope}/providers/Microsoft.Resources/tags/default
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['GET'])
def tags_getatscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_getatscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_GetAtScope", "path_params": kwargs}), 501

# Operation: Tags_DeleteAtScope
# Path: /{scope}/providers/Microsoft.Resources/tags/default
@bp.route('/<scope>/providers/Microsoft.Resources/tags/default', methods=['DELETE'])
def tags_deleteatscope(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.tags_deleteatscope(
    #         subscription_id=kwargs.get('subscriptionId'),
    #         resource_group=kwargs.get('resourceGroupName'),
    #         resource_name=kwargs.get('resourceName'),
    #         parameters=request.get_json(silent=True) or {},
    #         **kwargs
    #     ))
    #     return jsonify(result)
    # except NotImplementedError:
    #     return jsonify({"error": "Not implemented"}), 501
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Generated route for Tags_DeleteAtScope", "path_params": kwargs}), 501
