# mazure/sync/compatibility.py
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from datetime import datetime

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
