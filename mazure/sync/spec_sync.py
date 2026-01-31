# mazure/sync/spec_sync.py
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from datetime import datetime
import git
import json
from dataclasses import dataclass
from enum import Enum

class SpecChangeType(Enum):
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"
    API_VERSION_ADDED = "api_version_added"
    API_VERSION_DEPRECATED = "api_version_deprecated"

@dataclass
class SpecChange:
    """Represents a change in Azure API specifications"""
    change_type: SpecChangeType
    provider: str
    resource_type: str
    api_version: str
    spec_path: Path
    details: Dict[str, Any]
    timestamp: datetime

class AzureSpecSyncEngine:
    """
    Synchronizes Mazure with official Azure REST API specifications
    Uses azure-rest-api-specs as source of truth
    """

    def __init__(
        self,
        specs_repo_path: Path,
        mazure_root: Path,
        github_token: Optional[str] = None
    ):
        self.specs_repo_path = specs_repo_path
        self.mazure_root = mazure_root
        self.github_token = github_token
        self.repo: Optional[git.Repo] = None
        self.change_log: List[SpecChange] = []

    async def initialize(self):
        """Initialize or clone azure-rest-api-specs repository"""

        if not self.specs_repo_path.exists():
            print("Cloning azure-rest-api-specs repository...")
            self.repo = git.Repo.clone_from(
                "https://github.com/Azure/azure-rest-api-specs.git",
                self.specs_repo_path,
                depth=1  # Shallow clone for speed
            )
        else:
            self.repo = git.Repo(self.specs_repo_path)

        print(f"Specs repository initialized at {self.specs_repo_path}")

    async def sync(self) -> List[SpecChange]:
        """
        Sync with latest Azure specifications
        Returns list of changes detected
        """

        if not self.repo:
            await self.initialize()

        # Store current HEAD
        old_commit = self.repo.head.commit

        # Pull latest changes
        print("Fetching latest Azure API specifications...")
        origin = self.repo.remotes.origin
        origin.pull('main')

        new_commit = self.repo.head.commit

        # Detect changes
        if old_commit != new_commit:
            print(f"Changes detected: {old_commit.hexsha[:7]} -> {new_commit.hexsha[:7]}")
            self.change_log = await self._analyze_changes(old_commit, new_commit)

            # Generate update tasks
            await self._generate_update_tasks(self.change_log)

            return self.change_log
        else:
            print("No changes detected in Azure API specifications")
            return []

    async def _analyze_changes(
        self,
        old_commit: git.Commit,
        new_commit: git.Commit
    ) -> List[SpecChange]:
        """Analyze git diff to identify API specification changes"""

        changes = []

        # Get diff between commits
        diff_index = old_commit.diff(new_commit)

        for diff_item in diff_index:
            # Only process OpenAPI spec files
            if not self._is_openapi_file(diff_item.b_path if diff_item.b_path else diff_item.a_path):
                continue

            change = await self._parse_diff_item(diff_item)
            if change:
                changes.append(change)

        print(f"Analyzed {len(changes)} specification changes")
        return changes

    def _is_openapi_file(self, path: str) -> bool:
        """Check if file is an OpenAPI specification"""
        return (
            path.endswith('.json') and
            '/specification/' in path and
            ('stable' in path or 'preview' in path)
        )

    async def _parse_diff_item(self, diff_item) -> Optional[SpecChange]:
        """Parse a git diff item into a SpecChange"""

        # Determine change type
        if diff_item.new_file:
            change_type = SpecChangeType.ADDED
            path = diff_item.b_path
        elif diff_item.deleted_file:
            change_type = SpecChangeType.REMOVED
            path = diff_item.a_path
        else:
            change_type = SpecChangeType.MODIFIED
            path = diff_item.b_path

        # Parse path to extract provider, resource type, API version
        # Path format: specification/{provider}/{stability}/{api-version}/{resource}.json
        parts = Path(path).parts

        if len(parts) < 5:
            return None

        try:
            spec_idx = parts.index('specification')
            provider = parts[spec_idx + 1]
            stability = parts[spec_idx + 2]  # 'stable' or 'preview'
            api_version = parts[spec_idx + 3]
            resource_file = parts[spec_idx + 4]
            resource_type = resource_file.replace('.json', '')
        except (ValueError, IndexError):
            return None

        return SpecChange(
            change_type=change_type,
            provider=provider,
            resource_type=resource_type,
            api_version=api_version,
            spec_path=Path(path),
            details={
                'stability': stability,
                'file': resource_file,
                'additions': diff_item.diff.decode('utf-8', errors='ignore') if hasattr(diff_item, 'diff') else None
            },
            timestamp=datetime.utcnow()
        )

    async def _generate_update_tasks(self, changes: List[SpecChange]):
        """Generate code update tasks based on specification changes"""

        tasks_file = self.mazure_root / "sync" / "pending_updates.json"
        tasks_file.parent.mkdir(parents=True, exist_ok=True)

        tasks = []
        for change in changes:
            task = {
                'id': f"{change.provider}_{change.resource_type}_{change.api_version}",
                'change_type': change.change_type.value,
                'provider': change.provider,
                'resource_type': change.resource_type,
                'api_version': change.api_version,
                'spec_path': str(change.spec_path),
                'timestamp': change.timestamp.isoformat(),
                'status': 'pending',
                'auto_generated': False
            }
            tasks.append(task)

        # Load existing tasks
        existing_tasks = []
        if tasks_file.exists():
            with open(tasks_file) as f:
                existing_tasks = json.load(f)

        # Merge with new tasks
        existing_ids = {t['id'] for t in existing_tasks}
        for task in tasks:
            if task['id'] not in existing_ids:
                existing_tasks.append(task)

        # Save updated tasks
        with open(tasks_file, 'w') as f:
            json.dump(existing_tasks, f, indent=2)

        print(f"Generated {len(tasks)} update tasks")

    async def get_service_coverage(self) -> Dict[str, Any]:
        """
        Analyze what percentage of Azure services are implemented in Mazure
        """

        # Scan azure-rest-api-specs for all providers
        spec_dir = self.specs_repo_path / "specification"
        all_providers = set()
        all_resource_types = {}

        if spec_dir.exists():
            for provider_dir in spec_dir.iterdir():
                if not provider_dir.is_dir():
                    continue

                provider_name = provider_dir.name
                all_providers.add(provider_name)

                # Count resource types and API versions
                resource_count = 0
                for stability in ['stable', 'preview']:
                    stability_dir = provider_dir / stability
                    if not stability_dir.exists():
                        continue

                    for version_dir in stability_dir.iterdir():
                        if not version_dir.is_dir():
                            continue

                        resource_count += len(list(version_dir.glob('*.json')))

                all_resource_types[provider_name] = resource_count

        # Check what's implemented in Mazure
        services_dir = self.mazure_root / "mazure" / "services"
        implemented_providers = set()

        if services_dir.exists():
            for service_dir in services_dir.iterdir():
                if service_dir.is_dir() and not service_dir.name.startswith('_'):
                    # Map directory name to provider namespace
                    provider_mapping = {
                        'compute': 'Microsoft.Compute',
                        'network': 'Microsoft.Network',
                        'storage': 'Microsoft.Storage',
                        'resources': 'Microsoft.Resources',
                        'authorization': 'Microsoft.Authorization',
                        'keyvault': 'Microsoft.KeyVault',
                        'web': 'Microsoft.Web',
                        'sql': 'Microsoft.Sql',
                    }

                    provider = provider_mapping.get(service_dir.name)
                    if provider:
                        implemented_providers.add(provider)

        coverage_percentage = (len(implemented_providers) / len(all_providers)) * 100 if len(all_providers) > 0 else 0

        return {
            'total_providers': len(all_providers),
            'implemented_providers': len(implemented_providers),
            'coverage_percentage': round(coverage_percentage, 2),
            'providers': {
                'all': sorted(list(all_providers)),
                'implemented': sorted(list(implemented_providers)),
                'missing': sorted(list(all_providers - implemented_providers))
            },
            'resource_types_by_provider': all_resource_types,
            'timestamp': datetime.utcnow().isoformat()
        }
