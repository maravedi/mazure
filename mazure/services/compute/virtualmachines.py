"""
Microsoft.Compute/virtualMachines Service Implementation
Auto-generated from Azure REST API specifications
Generated: 2026-02-01T02:13:49.635753
API Version: 2024-07-01
"""

from typing import Optional, Dict, Any, List
from mazure.core.state import StateManager
# from mazure.schemas.microsoft_compute import *

class VirtualmachinesService:
    """Implements Microsoft.Compute/virtualMachines API"""

    RESOURCE_TYPE = "Microsoft.Compute/virtualMachines"
    API_VERSIONS = ["2024-07-01"]

    def __init__(self, state: StateManager):
        self.state = state

    
    async def create_or_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        parameters: Dict[str, Any],
        api_version: str = "2024-07-01"
    ) -> Dict[str, Any]:
        """Create or update resource"""

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
        """List resources"""

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
        """Delete resource"""

        return await self.state.delete_resource(
            subscription_id, resource_group, self.RESOURCE_TYPE, resource_name
        )
    

    
    
    async def virtualmachineextensions_createorupdate(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to create or update the extension."""

        # TODO: Implement VirtualMachineExtensions_CreateOrUpdate
        raise NotImplementedError("VirtualMachineExtensions_CreateOrUpdate not yet implemented")
    
    
    
    async def virtualmachineextensions_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to update the extension."""

        # TODO: Implement VirtualMachineExtensions_Update
        raise NotImplementedError("VirtualMachineExtensions_Update not yet implemented")
    
    
    
    async def virtualmachineextensions_delete(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to delete the extension."""

        # TODO: Implement VirtualMachineExtensions_Delete
        raise NotImplementedError("VirtualMachineExtensions_Delete not yet implemented")
    
    
    
    async def virtualmachineextensions_get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to get the extension."""

        # TODO: Implement VirtualMachineExtensions_Get
        raise NotImplementedError("VirtualMachineExtensions_Get not yet implemented")
    
    
    
    async def virtualmachineextensions_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to get all extensions of a Virtual Machine."""

        # TODO: Implement VirtualMachineExtensions_List
        raise NotImplementedError("VirtualMachineExtensions_List not yet implemented")
    
    
    
    async def virtualmachines_listbylocation(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets all the virtual machines under the specified subscription for the specified location."""

        # TODO: Implement VirtualMachines_ListByLocation
        raise NotImplementedError("VirtualMachines_ListByLocation not yet implemented")
    
    
    
    async def virtualmachines_capture(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Captures the VM by copying virtual hard disks of the VM and outputs a template that can be used to create similar VMs."""

        # TODO: Implement VirtualMachines_Capture
        raise NotImplementedError("VirtualMachines_Capture not yet implemented")
    
    
    
    
    
    async def virtualmachines_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to update a virtual machine."""

        # TODO: Implement VirtualMachines_Update
        raise NotImplementedError("VirtualMachines_Update not yet implemented")
    
    
    
    
    
    async def virtualmachines_get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Retrieves information about the model view or the instance view of a virtual machine."""

        # TODO: Implement VirtualMachines_Get
        raise NotImplementedError("VirtualMachines_Get not yet implemented")
    
    
    
    async def virtualmachines_instanceview(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Retrieves information about the run-time state of a virtual machine."""

        # TODO: Implement VirtualMachines_InstanceView
        raise NotImplementedError("VirtualMachines_InstanceView not yet implemented")
    
    
    
    async def virtualmachines_converttomanageddisks(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Converts virtual machine disks from blob-based to managed disks. Virtual machine must be stop-deallocated before invoking this operation."""

        # TODO: Implement VirtualMachines_ConvertToManagedDisks
        raise NotImplementedError("VirtualMachines_ConvertToManagedDisks not yet implemented")
    
    
    
    async def virtualmachines_deallocate(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Shuts down the virtual machine and releases the compute resources. You are not billed for the compute resources that this virtual machine uses."""

        # TODO: Implement VirtualMachines_Deallocate
        raise NotImplementedError("VirtualMachines_Deallocate not yet implemented")
    
    
    
    async def virtualmachines_generalize(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Sets the OS state of the virtual machine to generalized. It is recommended to sysprep the virtual machine before performing this operation. For Windows, please refer to [Create a managed image of a generalized VM in Azure](https://docs.microsoft.com/azure/virtual-machines/windows/capture-image-resource). For Linux, please refer to [How to create an image of a virtual machine or VHD](https://docs.microsoft.com/azure/virtual-machines/linux/capture-image)."""

        # TODO: Implement VirtualMachines_Generalize
        raise NotImplementedError("VirtualMachines_Generalize not yet implemented")
    
    
    
    async def virtualmachines_list(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Lists all of the virtual machines in the specified resource group. Use the nextLink property in the response to get the next page of virtual machines."""

        # TODO: Implement VirtualMachines_List
        raise NotImplementedError("VirtualMachines_List not yet implemented")
    
    
    
    async def virtualmachines_listall(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Lists all of the virtual machines in the specified subscription. Use the nextLink property in the response to get the next page of virtual machines."""

        # TODO: Implement VirtualMachines_ListAll
        raise NotImplementedError("VirtualMachines_ListAll not yet implemented")
    
    
    
    
    
    async def virtualmachines_poweroff(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to power off (stop) a virtual machine. The virtual machine can be restarted with the same provisioned resources. You are still charged for this virtual machine. NOTE: This operation is not allowed on a virtual machine that is being deallocated or has already been deallocated."""

        # TODO: Implement VirtualMachines_PowerOff
        raise NotImplementedError("VirtualMachines_PowerOff not yet implemented")
    
    
    
    async def virtualmachines_reapply(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to reapply a virtual machine's state."""

        # TODO: Implement VirtualMachines_Reapply
        raise NotImplementedError("VirtualMachines_Reapply not yet implemented")
    
    
    
    async def virtualmachines_restart(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to restart a virtual machine."""

        # TODO: Implement VirtualMachines_Restart
        raise NotImplementedError("VirtualMachines_Restart not yet implemented")
    
    
    
    async def virtualmachines_start(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to start a virtual machine."""

        # TODO: Implement VirtualMachines_Start
        raise NotImplementedError("VirtualMachines_Start not yet implemented")
    
    
    
    async def virtualmachines_redeploy(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Shuts down the virtual machine, moves it to a new node, and powers it back on."""

        # TODO: Implement VirtualMachines_Redeploy
        raise NotImplementedError("VirtualMachines_Redeploy not yet implemented")
    
    
    
    async def virtualmachines_reimage(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Reimages (upgrade the operating system) a virtual machine which don't have a ephemeral OS disk, for virtual machines who have a ephemeral OS disk the virtual machine is reset to initial state. NOTE: The retaining of old OS disk depends on the value of deleteOption of OS disk. If deleteOption is detach, the old OS disk will be preserved after reimage. If deleteOption is delete, the old OS disk will be deleted after reimage. The deleteOption of the OS disk should be updated accordingly before performing the reimage."""

        # TODO: Implement VirtualMachines_Reimage
        raise NotImplementedError("VirtualMachines_Reimage not yet implemented")
    
    
    
    async def virtualmachines_retrievebootdiagnosticsdata(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to retrieve SAS URIs for a virtual machine's boot diagnostic logs."""

        # TODO: Implement VirtualMachines_RetrieveBootDiagnosticsData
        raise NotImplementedError("VirtualMachines_RetrieveBootDiagnosticsData not yet implemented")
    
    
    
    async def virtualmachines_performmaintenance(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to perform maintenance on a virtual machine."""

        # TODO: Implement VirtualMachines_PerformMaintenance
        raise NotImplementedError("VirtualMachines_PerformMaintenance not yet implemented")
    
    
    
    async def virtualmachines_simulateeviction(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """The operation to simulate the eviction of spot virtual machine."""

        # TODO: Implement VirtualMachines_SimulateEviction
        raise NotImplementedError("VirtualMachines_SimulateEviction not yet implemented")
    
    
    
    async def virtualmachines_assesspatches(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Assess patches on the VM."""

        # TODO: Implement VirtualMachines_AssessPatches
        raise NotImplementedError("VirtualMachines_AssessPatches not yet implemented")
    
    
    
    async def virtualmachines_installpatches(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Installs patches on the VM."""

        # TODO: Implement VirtualMachines_InstallPatches
        raise NotImplementedError("VirtualMachines_InstallPatches not yet implemented")
    
    
    
    async def virtualmachines_attachdetachdatadisks(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Attach and detach data disks to/from the virtual machine."""

        # TODO: Implement VirtualMachines_AttachDetachDataDisks
        raise NotImplementedError("VirtualMachines_AttachDetachDataDisks not yet implemented")
    
    