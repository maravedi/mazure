"""
API Routes for Microsoft.Compute/virtualMachines
Generated: 2026-02-01T02:13:49.657697
"""

from flask import Blueprint, request, jsonify
from mazure.core.state import StateManager
from mazure.services.compute.virtualmachines import VirtualmachinesService
import asyncio

bp = Blueprint('microsoft_compute_virtualmachines', __name__)
state = StateManager()
service = VirtualmachinesService(state)

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Operation: VirtualMachineExtensions_CreateOrUpdate
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/extensions/{vmExtensionName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/extensions/<vmExtensionName>', methods=['PUT'])
def virtualmachineextensions_createorupdate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachineextensions_createorupdate(
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

    return jsonify({"message": "Generated route for VirtualMachineExtensions_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: VirtualMachineExtensions_Update
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/extensions/{vmExtensionName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/extensions/<vmExtensionName>', methods=['PATCH'])
def virtualmachineextensions_update(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachineextensions_update(
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

    return jsonify({"message": "Generated route for VirtualMachineExtensions_Update", "path_params": kwargs}), 501

# Operation: VirtualMachineExtensions_Delete
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/extensions/{vmExtensionName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/extensions/<vmExtensionName>', methods=['DELETE'])
def virtualmachineextensions_delete(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachineextensions_delete(
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

    return jsonify({"message": "Generated route for VirtualMachineExtensions_Delete", "path_params": kwargs}), 501

# Operation: VirtualMachineExtensions_Get
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/extensions/{vmExtensionName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/extensions/<vmExtensionName>', methods=['GET'])
def virtualmachineextensions_get(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachineextensions_get(
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

    return jsonify({"message": "Generated route for VirtualMachineExtensions_Get", "path_params": kwargs}), 501

# Operation: VirtualMachineExtensions_List
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/extensions
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/extensions', methods=['GET'])
def virtualmachineextensions_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachineextensions_list(
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

    return jsonify({"message": "Generated route for VirtualMachineExtensions_List", "path_params": kwargs}), 501

# Operation: VirtualMachines_ListByLocation
# Path: /subscriptions/{subscriptionId}/providers/Microsoft.Compute/locations/{location}/virtualMachines
@bp.route('/subscriptions/<subscriptionId>/providers/Microsoft.Compute/locations/<location>/virtualMachines', methods=['GET'])
def virtualmachines_listbylocation(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_listbylocation(
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

    return jsonify({"message": "Generated route for VirtualMachines_ListByLocation", "path_params": kwargs}), 501

# Operation: VirtualMachines_Capture
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/capture
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/capture', methods=['POST'])
def virtualmachines_capture(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_capture(
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

    return jsonify({"message": "Generated route for VirtualMachines_Capture", "path_params": kwargs}), 501

# Operation: VirtualMachines_CreateOrUpdate
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>', methods=['PUT'])
def virtualmachines_createorupdate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_createorupdate(
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

    return jsonify({"message": "Generated route for VirtualMachines_CreateOrUpdate", "path_params": kwargs}), 501

# Operation: VirtualMachines_Update
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>', methods=['PATCH'])
def virtualmachines_update(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_update(
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

    return jsonify({"message": "Generated route for VirtualMachines_Update", "path_params": kwargs}), 501

# Operation: VirtualMachines_Delete
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>', methods=['DELETE'])
def virtualmachines_delete(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_delete(
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

    return jsonify({"message": "Generated route for VirtualMachines_Delete", "path_params": kwargs}), 501

# Operation: VirtualMachines_Get
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>', methods=['GET'])
def virtualmachines_get(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_get(
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

    return jsonify({"message": "Generated route for VirtualMachines_Get", "path_params": kwargs}), 501

# Operation: VirtualMachines_InstanceView
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/instanceView
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/instanceView', methods=['GET'])
def virtualmachines_instanceview(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_instanceview(
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

    return jsonify({"message": "Generated route for VirtualMachines_InstanceView", "path_params": kwargs}), 501

# Operation: VirtualMachines_ConvertToManagedDisks
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/convertToManagedDisks
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/convertToManagedDisks', methods=['POST'])
def virtualmachines_converttomanageddisks(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_converttomanageddisks(
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

    return jsonify({"message": "Generated route for VirtualMachines_ConvertToManagedDisks", "path_params": kwargs}), 501

# Operation: VirtualMachines_Deallocate
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/deallocate
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/deallocate', methods=['POST'])
def virtualmachines_deallocate(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_deallocate(
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

    return jsonify({"message": "Generated route for VirtualMachines_Deallocate", "path_params": kwargs}), 501

# Operation: VirtualMachines_Generalize
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/generalize
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/generalize', methods=['POST'])
def virtualmachines_generalize(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_generalize(
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

    return jsonify({"message": "Generated route for VirtualMachines_Generalize", "path_params": kwargs}), 501

# Operation: VirtualMachines_List
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines', methods=['GET'])
def virtualmachines_list(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_list(
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

    return jsonify({"message": "Generated route for VirtualMachines_List", "path_params": kwargs}), 501

# Operation: VirtualMachines_ListAll
# Path: /subscriptions/{subscriptionId}/providers/Microsoft.Compute/virtualMachines
@bp.route('/subscriptions/<subscriptionId>/providers/Microsoft.Compute/virtualMachines', methods=['GET'])
def virtualmachines_listall(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_listall(
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

    return jsonify({"message": "Generated route for VirtualMachines_ListAll", "path_params": kwargs}), 501

# Operation: VirtualMachines_ListAvailableSizes
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/vmSizes
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/vmSizes', methods=['GET'])
def virtualmachines_listavailablesizes(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_listavailablesizes(
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

    return jsonify({"message": "Generated route for VirtualMachines_ListAvailableSizes", "path_params": kwargs}), 501

# Operation: VirtualMachines_PowerOff
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/powerOff
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/powerOff', methods=['POST'])
def virtualmachines_poweroff(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_poweroff(
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

    return jsonify({"message": "Generated route for VirtualMachines_PowerOff", "path_params": kwargs}), 501

# Operation: VirtualMachines_Reapply
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/reapply
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/reapply', methods=['POST'])
def virtualmachines_reapply(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_reapply(
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

    return jsonify({"message": "Generated route for VirtualMachines_Reapply", "path_params": kwargs}), 501

# Operation: VirtualMachines_Restart
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/restart
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/restart', methods=['POST'])
def virtualmachines_restart(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_restart(
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

    return jsonify({"message": "Generated route for VirtualMachines_Restart", "path_params": kwargs}), 501

# Operation: VirtualMachines_Start
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/start
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/start', methods=['POST'])
def virtualmachines_start(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_start(
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

    return jsonify({"message": "Generated route for VirtualMachines_Start", "path_params": kwargs}), 501

# Operation: VirtualMachines_Redeploy
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/redeploy
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/redeploy', methods=['POST'])
def virtualmachines_redeploy(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_redeploy(
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

    return jsonify({"message": "Generated route for VirtualMachines_Redeploy", "path_params": kwargs}), 501

# Operation: VirtualMachines_Reimage
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/reimage
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/reimage', methods=['POST'])
def virtualmachines_reimage(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_reimage(
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

    return jsonify({"message": "Generated route for VirtualMachines_Reimage", "path_params": kwargs}), 501

# Operation: VirtualMachines_RetrieveBootDiagnosticsData
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/retrieveBootDiagnosticsData
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/retrieveBootDiagnosticsData', methods=['POST'])
def virtualmachines_retrievebootdiagnosticsdata(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_retrievebootdiagnosticsdata(
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

    return jsonify({"message": "Generated route for VirtualMachines_RetrieveBootDiagnosticsData", "path_params": kwargs}), 501

# Operation: VirtualMachines_PerformMaintenance
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/performMaintenance
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/performMaintenance', methods=['POST'])
def virtualmachines_performmaintenance(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_performmaintenance(
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

    return jsonify({"message": "Generated route for VirtualMachines_PerformMaintenance", "path_params": kwargs}), 501

# Operation: VirtualMachines_SimulateEviction
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/simulateEviction
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/simulateEviction', methods=['POST'])
def virtualmachines_simulateeviction(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_simulateeviction(
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

    return jsonify({"message": "Generated route for VirtualMachines_SimulateEviction", "path_params": kwargs}), 501

# Operation: VirtualMachines_AssessPatches
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/assessPatches
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/assessPatches', methods=['POST'])
def virtualmachines_assesspatches(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_assesspatches(
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

    return jsonify({"message": "Generated route for VirtualMachines_AssessPatches", "path_params": kwargs}), 501

# Operation: VirtualMachines_InstallPatches
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/installPatches
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/installPatches', methods=['POST'])
def virtualmachines_installpatches(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_installpatches(
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

    return jsonify({"message": "Generated route for VirtualMachines_InstallPatches", "path_params": kwargs}), 501

# Operation: VirtualMachines_AttachDetachDataDisks
# Path: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}/attachDetachDataDisks
@bp.route('/subscriptions/<subscriptionId>/resourceGroups/<resourceGroupName>/providers/Microsoft.Compute/virtualMachines/<vmName>/attachDetachDataDisks', methods=['POST'])
def virtualmachines_attachdetachdatadisks(**kwargs):
    # This is a stub implementation
    # Arguments from path are in kwargs

    # We would need to map kwargs to service arguments here
    # subscriptionId -> subscription_id
    # resourceGroupName -> resource_group

    # Example of how to call the async service:
    # try:
    #     result = run_async(service.virtualmachines_attachdetachdatadisks(
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

    return jsonify({"message": "Generated route for VirtualMachines_AttachDetachDataDisks", "path_params": kwargs}), 501
