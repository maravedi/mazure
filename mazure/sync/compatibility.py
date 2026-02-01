# mazure/sync/compatibility.py
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class APIVersionInfo:
    """Information about an API version"""
    version: str
    status: str  # 'stable', 'preview', 'deprecated'
    release_date: datetime
    deprecation_date: Optional[datetime]
    breaking_changes: List[str]
    supported_in_mazure: bool

class CompatibilityMatrix:
    """
    Tracks Azure API version compatibility and lifecycle
    """

    def __init__(self):
        self.api_versions: Dict[str, Dict[str, APIVersionInfo]] = {}

    def register_api_version(
        self,
        provider: str,
        resource_type: str,
        version_info: APIVersionInfo
    ):
        """Register API version information"""

        key = f"{provider}/{resource_type}"
        if key not in self.api_versions:
            self.api_versions[key] = {}

        self.api_versions[key][version_info.version] = version_info

    def load_from_specs(self, specs_path: Path, mazure_root: Path):
        """
        Scan Azure specs and Mazure codebase to populate compatibility matrix
        """
        spec_dir = specs_path / "specification"
        if not spec_dir.exists():
            print(f"Warning: Specs directory {spec_dir} does not exist.")
            return

        for service_dir in spec_dir.iterdir():
            if not service_dir.is_dir():
                continue

            # Handle resource-manager structure (specification/service/resource-manager/provider)
            rm_dir = service_dir / "resource-manager"
            if rm_dir.exists():
                provider_dirs = [d for d in rm_dir.iterdir() if d.is_dir()]
            else:
                # Fallback for flat structure
                provider_dirs = [service_dir]

            for provider_dir in provider_dirs:
                provider = provider_dir.name

                # Map provider to Mazure service package
                service_pkg = self._get_service_package_name(provider)
                service_dir = mazure_root / "mazure" / "services" / service_pkg

                for stability in ['stable', 'preview']:
                    stability_dir = provider_dir / stability
                    if not stability_dir.exists():
                        continue

                    for version_dir in stability_dir.iterdir():
                        if not version_dir.is_dir():
                            continue

                        api_version = version_dir.name

                        for spec_file in version_dir.glob('*.json'):
                            resource_type = spec_file.stem

                            # Check if supported in Mazure
                            # We assume if the service file exists, it supports at least some version.
                            # Ideally we should check if the specific version is supported,
                            # but for now existence of service file implies support.
                            # Note: Generated services store API_VERSIONS list, manual ones might not.
                            is_supported = False

                            # Check for generated service
                            if service_dir.exists() and (service_dir / f"{resource_type.lower()}.py").exists():
                                is_supported = True

                            # Check for manual mapping (heuristic)
                            elif self._check_manual_support(service_pkg, resource_type):
                                is_supported = True

                            self.register_api_version(
                                provider=provider,
                                resource_type=resource_type,
                                version_info=APIVersionInfo(
                                    version=api_version,
                                    status=stability,
                                    release_date=datetime.utcnow(), # Placeholder as we don't parse git history here
                                    deprecation_date=None,
                                    breaking_changes=[],
                                    supported_in_mazure=is_supported
                                )
                            )

    def _get_service_package_name(self, provider: str) -> str:
        """Get the package name for the provider"""
        provider_mapping = {
            'Microsoft.Compute': 'compute',
            'Microsoft.Network': 'network',
            'Microsoft.Storage': 'storage',
            'Microsoft.Resources': 'resources',
            'Microsoft.Authorization': 'authorization',
            'Microsoft.KeyVault': 'keyvault',
            'Microsoft.Web': 'web',
            'Microsoft.Sql': 'sql',
        }
        return provider_mapping.get(provider, provider.lower().replace('microsoft.', ''))

    def _check_manual_support(self, service_pkg: str, resource_type: str) -> bool:
        """Check if resource is supported by manual implementation"""
        # This is a basic mapping based on known manual implementations
        if service_pkg == 'compute' and resource_type.lower() in ['virtualmachines']:
            return True
        if service_pkg == 'resources' and resource_type.lower() in ['resourcegroups']:
            return True
        if service_pkg == 'storage' and resource_type.lower() in ['storageaccounts']:
            return True
        return False

    def get_supported_versions(
        self,
        provider: str,
        resource_type: str
    ) -> List[str]:
        """Get list of API versions supported by Mazure"""

        key = f"{provider}/{resource_type}"
        if key not in self.api_versions:
            return []

        return [
            v.version
            for v in self.api_versions[key].values()
            if v.supported_in_mazure and v.status != 'deprecated'
        ]

    def check_version_compatibility(
        self,
        provider: str,
        resource_type: str,
        requested_version: str
    ) -> Dict[str, Any]:
        """
        Check if requested API version is compatible
        Returns compatibility info and recommendations
        """

        key = f"{provider}/{resource_type}"

        if key not in self.api_versions:
            return {
                'compatible': False,
                'reason': 'Resource type not supported',
                'recommendation': 'Open an issue on GitHub'
            }

        if requested_version in self.api_versions[key]:
            version_info = self.api_versions[key][requested_version]

            if version_info.status == 'deprecated':
                return {
                    'compatible': True,
                    'warning': f'API version {requested_version} is deprecated',
                    'recommendation': f'Migrate to latest version',
                    'latest_version': self._get_latest_version(key)
                }

            if not version_info.supported_in_mazure:
                return {
                    'compatible': False,
                    'reason': f'API version {requested_version} not yet implemented in Mazure',
                    'recommendation': 'Use a different version or wait for implementation',
                    'supported_versions': self.get_supported_versions(provider, resource_type)
                }

            return {'compatible': True}
        else:
            return {
                'compatible': False,
                'reason': f'Unknown API version: {requested_version}',
                'recommendation': 'Check Azure documentation for valid versions',
                'supported_versions': self.get_supported_versions(provider, resource_type)
            }

    def _get_latest_version(self, resource_key: str) -> Optional[str]:
        """Get latest stable API version for a resource"""

        stable_versions = [
            v for v in self.api_versions[resource_key].values()
            if v.status == 'stable' and v.supported_in_mazure
        ]

        if not stable_versions:
            return None

        return sorted(stable_versions, key=lambda v: v.version, reverse=True)[0].version

    def generate_compatibility_report(self) -> Dict[str, Any]:
        """Generate comprehensive compatibility report"""

        report = {
            'total_resource_types': len(self.api_versions),
            'coverage_by_provider': {},
            'deprecated_versions': [],
            'preview_versions': [],
            'recommendations': []
        }

        for resource_key, versions in self.api_versions.items():
            provider = resource_key.split('/')[0]

            if provider not in report['coverage_by_provider']:
                report['coverage_by_provider'][provider] = {
                    'total': 0,
                    'supported': 0,
                    'coverage_percentage': 0
                }

            report['coverage_by_provider'][provider]['total'] += 1

            has_support = any(v.supported_in_mazure for v in versions.values())
            if has_support:
                report['coverage_by_provider'][provider]['supported'] += 1

            # Check for deprecated versions still in use
            for version, info in versions.items():
                if info.status == 'deprecated' and info.supported_in_mazure:
                    report['deprecated_versions'].append({
                        'resource': resource_key,
                        'version': version,
                        'deprecation_date': info.deprecation_date.isoformat() if info.deprecation_date else None
                    })
                elif info.status == 'preview' and info.supported_in_mazure:
                    report['preview_versions'].append({
                        'resource': resource_key,
                        'version': version
                    })

        # Calculate coverage percentages
        for provider_data in report['coverage_by_provider'].values():
            if provider_data['total'] > 0:
                provider_data['coverage_percentage'] = round(
                    (provider_data['supported'] / provider_data['total']) * 100, 2
                )

        return report
