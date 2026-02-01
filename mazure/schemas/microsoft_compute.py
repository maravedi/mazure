
"""
Pydantic schemas for Microsoft.Compute
Generated: 2026-02-01T02:12:42.554005
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel



class RetrieveBootDiagnosticsDataResult(BaseModel):
    """The SAS URIs of the console screenshot and serial log blobs."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtensionInstanceView(BaseModel):
    """The instance view of a virtual machine extension."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtensionProperties(BaseModel):
    """Describes the properties of a Virtual Machine Extension."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtensionUpdateProperties(BaseModel):
    """Describes the properties of a Virtual Machine Extension."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtension(BaseModel):
    """Describes a Virtual Machine Extension."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtensionUpdate(BaseModel):
    """Describes a Virtual Machine Extension."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtensionsListResult(BaseModel):
    """The List Extension operation response"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineSoftwarePatchProperties(BaseModel):
    """Describes the properties of a Virtual Machine software patch."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineAssessPatchesResult(BaseModel):
    """Describes the properties of an AssessPatches result."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineInstallPatchesParameters(BaseModel):
    """Input for InstallPatches as directly received by the API"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class WindowsParameters(BaseModel):
    """Input for InstallPatches on a Windows VM, as directly received by the API"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class LinuxParameters(BaseModel):
    """Input for InstallPatches on a Linux VM, as directly received by the API"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineInstallPatchesResult(BaseModel):
    """The result summary of an installation operation."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class PatchInstallationDetail(BaseModel):
    """Information about a specific patch that was encountered during an installation action."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineReimageParameters(BaseModel):
    """Parameters for Reimaging Virtual Machine. NOTE: Virtual Machine OS disk will always be reimaged"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class OSProfileProvisioningData(BaseModel):
    """Additional parameters for Reimaging Non-Ephemeral Virtual Machine."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineCaptureParameters(BaseModel):
    """Capture Virtual Machine parameters."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineCaptureResult(BaseModel):
    """Output of virtual machine capture operation."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineIpTag(BaseModel):
    """Contains the IP tag associated with the public IP address."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachinePublicIPAddressDnsSettingsConfiguration(BaseModel):
    """Describes a virtual machines network configuration's DNS settings."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachinePublicIPAddressConfigurationProperties(BaseModel):
    """Describes a virtual machines IP Configuration's PublicIPAddress configuration"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachinePublicIPAddressConfiguration(BaseModel):
    """Describes a virtual machines IP Configuration's PublicIPAddress configuration"""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineNetworkInterfaceIPConfigurationProperties(BaseModel):
    """Describes a virtual machine network interface IP configuration properties."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineNetworkInterfaceIPConfiguration(BaseModel):
    """Describes a virtual machine network profile's IP configuration."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineNetworkInterfaceDnsSettingsConfiguration(BaseModel):
    """Describes a virtual machines network configuration's DNS settings."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineNetworkInterfaceConfigurationProperties(BaseModel):
    """Describes a virtual machine network profile's IP configuration."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineNetworkInterfaceConfiguration(BaseModel):
    """Describes a virtual machine network interface configurations."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineExtensionHandlerInstanceView(BaseModel):
    """The instance view of a virtual machine extension handler."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineAgentInstanceView(BaseModel):
    """The instance view of the VM Agent running on the virtual machine."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineIdentity(BaseModel):
    """Identity for the virtual machine."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineInstanceView(BaseModel):
    """The instance view of a virtual machine."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineProperties(BaseModel):
    """Describes the properties of a Virtual Machine."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachine(BaseModel):
    """Describes a Virtual Machine."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineUpdate(BaseModel):
    """Describes a Virtual Machine Update."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineListResult(BaseModel):
    """The List Virtual Machine operation response."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachineHealthStatus(BaseModel):
    """The health status of the VM."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class VirtualMachinePatchStatus(BaseModel):
    """The status of virtual machine patch operations."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class AvailablePatchSummary(BaseModel):
    """Describes the properties of an virtual machine instance view for available patch summary."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types


class LastPatchInstallationSummary(BaseModel):
    """Describes the properties of the last installed patch summary."""
    pass
    # Properties generation skipped for simplicity in this MVP
    # Ideally we would iterate over properties and map types

