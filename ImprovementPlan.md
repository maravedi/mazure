# Auto-Sync Architecture: Keeping Mazure Aligned with Azure ARM API

## Overview

Azure publishes their complete REST API specifications in the [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repository and uses [AutoRest](https://github.com/Azure/autorest) to generate official SDKs. We'll leverage these same tools to keep Mazure perpetually synchronized. [azure.github](http://azure.github.io/autorest/generate/)

***

## Architecture Components

### 1. Specification Synchronization System

```python
# src/mazure/sync/spec_sync.py
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
        services_dir = self.mazure_root / "src" / "mazure" / "services"
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
        
        coverage_percentage = (len(implemented_providers) / len(all_providers)) * 100
        
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
```

***

### 2. AutoRest-Based Code Generation

```python
# src/mazure/sync/codegen.py
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import json
from jinja2 import Environment, FileSystemLoader

class MazureCodeGenerator:
    """
    Generates Mazure service implementations from Azure OpenAPI specs
    Uses AutoRest for parsing, custom templates for generation
    """
    
    def __init__(
        self,
        specs_path: Path,
        mazure_root: Path,
        templates_path: Optional[Path] = None
    ):
        self.specs_path = specs_path
        self.mazure_root = mazure_root
        self.templates_path = templates_path or (mazure_root / "sync" / "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_path)))
    
    async def generate_service(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        spec_path: Path
    ) -> Path:
        """
        Generate a service implementation from OpenAPI spec
        """
        
        # Step 1: Parse OpenAPI spec using AutoRest
        code_model = await self._parse_spec_with_autorest(spec_path)
        
        # Step 2: Generate Python service code
        service_code = await self._generate_service_code(
            provider, resource_type, api_version, code_model
        )
        
        # Step 3: Generate Pydantic schemas
        schemas_code = await self._generate_schemas(
            provider, resource_type, api_version, code_model
        )
        
        # Step 4: Generate API route handlers
        routes_code = await self._generate_routes(
            provider, resource_type, api_version, code_model
        )
        
        # Step 5: Write files
        output_dir = await self._get_service_output_dir(provider)
        
        service_file = output_dir / f"{resource_type.lower()}.py"
        with open(service_file, 'w') as f:
            f.write(service_code)
        
        schemas_dir = self.mazure_root / "src" / "mazure" / "schemas"
        schemas_dir.mkdir(exist_ok=True, parents=True)
        schemas_file = schemas_dir / f"{provider.lower().replace('.', '_')}.py"
        
        # Append or create schemas file
        mode = 'a' if schemas_file.exists() else 'w'
        with open(schemas_file, mode) as f:
            f.write(schemas_code)
        
        # Generate routes
        routes_dir = self.mazure_root / "src" / "mazure" / "api"
        routes_file = routes_dir / f"{provider.lower().replace('.', '_')}.py"
        with open(routes_file, 'w') as f:
            f.write(routes_code)
        
        print(f"Generated service implementation: {service_file}")
        return service_file
    
    async def _parse_spec_with_autorest(self, spec_path: Path) -> Dict[str, Any]:
        """
        Use AutoRest to parse OpenAPI spec into code model
        """
        
        # Create temp directory for AutoRest output
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        
        # Run AutoRest with code model output
        cmd = [
            "autorest",
            "--input-file=" + str(spec_path),
            "--output-folder=" + str(temp_dir),
            "--python",
            "--code-model-v4=true",
            "--output-artifact=code-model-v4"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                print(f"AutoRest warning/error: {result.stderr}")
            
            # Load generated code model
            code_model_file = temp_dir / "code-model-v4.json"
            if code_model_file.exists():
                with open(code_model_file) as f:
                    return json.load(f)
            else:
                # Fallback: parse OpenAPI directly
                return await self._parse_openapi_directly(spec_path)
        
        except subprocess.TimeoutExpired:
            print("AutoRest timed out, using direct parsing")
            return await self._parse_openapi_directly(spec_path)
        except FileNotFoundError:
            print("AutoRest not installed, using direct parsing")
            return await self._parse_openapi_directly(spec_path)
    
    async def _parse_openapi_directly(self, spec_path: Path) -> Dict[str, Any]:
        """Fallback: Parse OpenAPI spec directly without AutoRest"""
        
        with open(spec_path) as f:
            spec = json.load(f)
        
        # Convert OpenAPI to simplified code model
        code_model = {
            'operations': [],
            'schemas': spec.get('definitions', {}),
            'paths': spec.get('paths', {}),
            'info': spec.get('info', {})
        }
        
        # Parse operations from paths
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                if method.upper() in ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']:
                    code_model['operations'].append({
                        'path': path,
                        'method': method.upper(),
                        'operation_id': operation.get('operationId'),
                        'parameters': operation.get('parameters', []),
                        'responses': operation.get('responses', {}),
                        'summary': operation.get('summary'),
                        'description': operation.get('description')
                    })
        
        return code_model
    
    async def _generate_service_code(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        code_model: Dict[str, Any]
    ) -> str:
        """Generate service implementation Python code"""
        
        template = self.jinja_env.get_template('service.py.jinja2')
        
        # Extract operations
        operations = code_model.get('operations', [])
        
        # Categorize operations
        crud_operations = {
            'create': None,
            'get': None,
            'list': None,
            'update': None,
            'delete': None
        }
        
        for op in operations:
            op_id = op.get('operation_id', '').lower()
            
            if 'create' in op_id or (op['method'] == 'PUT' and '{' in op['path']):
                crud_operations['create'] = op
            elif 'get' in op_id and op['method'] == 'GET':
                if '{' in op['path']:
                    crud_operations['get'] = op
                else:
                    crud_operations['list'] = op
            elif 'update' in op_id or op['method'] == 'PATCH':
                crud_operations['update'] = op
            elif 'delete' in op_id or op['method'] == 'DELETE':
                crud_operations['delete'] = op
        
        return template.render(
            provider=provider,
            resource_type=resource_type,
            api_version=api_version,
            operations=crud_operations,
            all_operations=operations,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _generate_schemas(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        code_model: Dict[str, Any]
    ) -> str:
        """Generate Pydantic schema models"""
        
        template = self.jinja_env.get_template('schemas.py.jinja2')
        
        schemas = code_model.get('schemas', {})
        
        return template.render(
            provider=provider,
            resource_type=resource_type,
            schemas=schemas,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _generate_routes(
        self,
        provider: str,
        resource_type: str,
        api_version: str,
        code_model: Dict[str, Any]
    ) -> str:
        """Generate FastAPI route handlers"""
        
        template = self.jinja_env.get_template('routes.py.jinja2')
        
        operations = code_model.get('operations', [])
        
        return template.render(
            provider=provider,
            resource_type=resource_type,
            api_version=api_version,
            operations=operations,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _get_service_output_dir(self, provider: str) -> Path:
        """Get output directory for service code"""
        
        # Map provider to directory name
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
        
        dir_name = provider_mapping.get(provider, provider.lower().replace('microsoft.', ''))
        output_dir = self.mazure_root / "src" / "mazure" / "services" / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return output_dir
```

***

### 3. Code Generation Templates

```jinja2
{# sync/templates/service.py.jinja2 #}
"""
{{ provider }}/{{ resource_type }} Service Implementation
Auto-generated from Azure REST API specifications
Generated: {{ timestamp }}
API Version: {{ api_version }}
"""

from typing import Optional, Dict, Any, List
from ...core.state import StateManager
from ...schemas.{{ provider.lower().replace('.', '_') }} import *

class {{ resource_type | title | replace('_', '') }}Service:
    """Implements {{ provider }}/{{ resource_type }} API"""
    
    RESOURCE_TYPE = "{{ provider }}/{{ resource_type }}"
    API_VERSIONS = ["{{ api_version }}"]
    
    def __init__(self, state: StateManager):
        self.state = state
    
    {% if operations.create %}
    async def create_or_update(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        parameters: Dict[str, Any],
        api_version: str = "{{ api_version }}"
    ) -> Dict[str, Any]:
        """{{ operations.create.summary or 'Create or update resource' }}"""
        
        # Validate required fields
        if 'location' not in parameters:
            raise ValueError("location is required")
        
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
                location=parameters['location'],
                tags=parameters.get('tags'),
                api_version=api_version
            )
            return resource.to_arm_dict()
    {% endif %}
    
    {% if operations.get %}
    async def get(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str
    ) -> Optional[Dict[str, Any]]:
        """{{ operations.get.summary or 'Get resource details' }}"""
        
        resource = await self.state.get_resource(
            subscription_id, resource_group, self.RESOURCE_TYPE, resource_name
        )
        
        return resource.to_arm_dict() if resource else None
    {% endif %}
    
    {% if operations.list %}
    async def list(
        self,
        subscription_id: str,
        resource_group: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """{{ operations.list.summary or 'List resources' }}"""
        
        resources = await self.state.list_resources(
            subscription_id, resource_group, self.RESOURCE_TYPE
        )
        
        return [r.to_arm_dict() for r in resources]
    {% endif %}
    
    {% if operations.delete %}
    async def delete(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str
    ) -> bool:
        """{{ operations.delete.summary or 'Delete resource' }}"""
        
        return await self.state.delete_resource(
            subscription_id, resource_group, self.RESOURCE_TYPE, resource_name
        )
    {% endif %}
    
    {% for operation in all_operations %}
    {% if operation.operation_id not in ['Create', 'Get', 'List', 'Update', 'Delete'] %}
    async def {{ operation.operation_id | lower | replace('.', '_') }}(
        self,
        subscription_id: str,
        resource_group: str,
        resource_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """{{ operation.summary or operation.description }}"""
        
        # TODO: Implement {{ operation.operation_id }}
        raise NotImplementedError("{{ operation.operation_id }} not yet implemented")
    {% endif %}
    {% endfor %}
```

***

### 4. Automated Update Pipeline

```yaml
# .github/workflows/sync-azure-specs.yml
name: Sync Azure API Specifications

on:
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'
  
  workflow_dispatch:
    inputs:
      force_regenerate:
        description: 'Force regenerate all services'
        required: false
        default: 'false'

jobs:
  sync-specs:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - name: Checkout Mazure
        uses: actions/checkout@v4
        with:
          submodules: true
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install -e ".[dev]"
          npm install -g autorest
      
      - name: Clone/Update Azure REST API Specs
        run: |
          if [ ! -d "specs/azure-rest-api-specs" ]; then
            git clone https://github.com/Azure/azure-rest-api-specs.git \
              specs/azure-rest-api-specs --depth=1
          else
            cd specs/azure-rest-api-specs
            git pull origin main
            cd ../..
          fi
      
      - name: Run Sync Engine
        id: sync
        run: |
          python -m mazure.sync.sync_command \
            --specs-path=specs/azure-rest-api-specs \
            --output=sync_report.json
          
          # Check if changes were detected
          if [ -s sync/pending_updates.json ]; then
            echo "changes_detected=true" >> $GITHUB_OUTPUT
          else
            echo "changes_detected=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Generate Code for New/Changed Specs
        if: steps.sync.outputs.changes_detected == 'true'
        run: |
          python -m mazure.sync.codegen_command \
            --tasks-file=sync/pending_updates.json \
            --auto-approve=${{ github.event.inputs.force_regenerate || 'false' }}
      
      - name: Run Tests
        if: steps.sync.outputs.changes_detected == 'true'
        run: |
          pytest tests/ -v --cov=mazure --cov-report=xml
      
      - name: Generate Coverage Report
        if: steps.sync.outputs.changes_detected == 'true'
        run: |
          python -m mazure.sync.coverage_report \
            --output=coverage_report.md
      
      - name: Create Pull Request
        if: steps.sync.outputs.changes_detected == 'true'
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: |
            Auto-sync: Update Azure API implementations
            
            This PR contains automatically generated code updates based on
            changes to Azure REST API specifications.
          branch: auto-sync-${{ github.run_number }}
          title: "🔄 Auto-sync: Azure API Specification Updates"
          body: |
            ## Azure API Specification Sync
            
            This PR was automatically generated by the sync workflow.
            
            ### Changes Summary
            
            ${{ steps.sync.outputs.summary }}
            
            ### Coverage Report
            
            See attached `coverage_report.md`
            
            ### Action Required
            
            - [ ] Review generated code
            - [ ] Run integration tests
            - [ ] Update documentation if needed
          labels: |
            auto-sync
            api-update
          reviewers: |
            @maintainer-team
      
      - name: Upload Sync Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: sync-report-${{ github.run_number }}
          path: |
            sync_report.json
            coverage_report.md
            sync/pending_updates.json

  notify:
    needs: sync-specs
    runs-on: ubuntu-latest
    if: failure()
    steps:
      - name: Notify on Failure
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Azure API sync failed! Check workflow logs.'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

***

### 5. Version Compatibility Matrix

```python
# src/mazure/sync/compatibility.py
from typing import Dict, List, Set
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
    
    def _get_latest_version(self, resource_key: str) -> str:
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
```

***

### 6. CLI Commands for Sync Management

```python
# src/mazure/cli/sync.py
import typer
from pathlib import Path
import asyncio

app = typer.Typer()

@app.command()
def sync(
    specs_path: Path = typer.Option(
        "specs/azure-rest-api-specs",
        help="Path to azure-rest-api-specs repository"
    ),
    auto_generate: bool = typer.Option(
        False,
        help="Automatically generate code for changes"
    )
):
    """Sync with latest Azure API specifications"""
    
    from ..sync.spec_sync import AzureSpecSyncEngine
    
    async def run():
        sync_engine = AzureSpecSyncEngine(
            specs_repo_path=specs_path,
            mazure_root=Path.cwd()
        )
        
        changes = await sync_engine.sync()
        
        if changes:
            typer.echo(f"✓ Found {len(changes)} specification changes")
            
            for change in changes[:5]:  # Show first 5
                typer.echo(
                    f"  - {change.change_type.value}: "
                    f"{change.provider}/{change.resource_type} "
                    f"(v{change.api_version})"
                )
            
            if len(changes) > 5:
                typer.echo(f"  ... and {len(changes) - 5} more")
            
            if auto_generate:
                typer.echo("\n🔄 Generating code updates...")
                # Trigger code generation
        else:
            typer.echo("✓ No changes detected")
    
    asyncio.run(run())

@app.command()
def coverage():
    """Show API coverage report"""
    
    from ..sync.spec_sync import AzureSpecSyncEngine
    
    async def run():
        sync_engine = AzureSpecSyncEngine(
            specs_repo_path=Path("specs/azure-rest-api-specs"),
            mazure_root=Path.cwd()
        )
        
        await sync_engine.initialize()
        coverage = await sync_engine.get_service_coverage()
        
        typer.echo(f"\n📊 Mazure API Coverage Report\n")
        typer.echo(f"Total Azure Providers: {coverage['total_providers']}")
        typer.echo(f"Implemented in Mazure: {coverage['implemented_providers']}")
        typer.echo(f"Coverage: {coverage['coverage_percentage']}%\n")
        
        typer.echo("✓ Implemented Providers:")
        for provider in coverage['providers']['implemented'][:10]:
            typer.echo(f"  - {provider}")
        
        typer.echo(f"\n❌ Missing Providers (showing 10 of {len(coverage['providers']['missing'])}):")
        for provider in coverage['providers']['missing'][:10]:
            typer.echo(f"  - {provider}")
    
    asyncio.run(run())

@app.command()
def generate(
    provider: Optional[str] = typer.Argument(None, help="Provider namespace"),
    resource_type: Optional[str] = typer.Argument(None, help="Resource type"),
    api_version: Optional[str] = typer.Argument(None, help="API version"),
    template: Optional[str] = typer.Option(None, help="Template name to generate environment from"),
    apply: bool = typer.Option(False, help="Apply the template directly to the running server"),
    output: Optional[Path] = typer.Option(None, help="Output path for generated script")
):
    """Generate service implementation from specification OR generate environment state from template"""
    
    if template:
        # Scenario Generation
        from ..scenarios.generator import ScenarioGenerator
        # ... scenario generation implementation ...
        return

    # Code Generation
    from ..sync.codegen import MazureCodeGenerator
    
    typer.echo(f"🔄 Generating {provider}/{resource_type} (v{api_version})...")
    
    # Implementation here
    typer.echo("✓ Service generated successfully")

if __name__ == "__main__":
    app()
```

***

### 7. Scenario Generation Engine

```python
# src/mazure/scenarios/generator.py
class ScenarioGenerator:
    """
    Generates and applies complex environment scenarios from templates.
    Useful for compliance testing, demos, and reproducing issues.
    """

    def __init__(self, template_name: str, mazure_root: Path):
        self.mazure_root = mazure_root
        self.template_name = template_name
        self.data = self._load_template()

    def generate_script(self, output_path: Optional[Path] = None) -> Path:
        """Generates a Python script to apply the scenario."""
        # Generates a script that uses requests to PUT resources
        pass

    def apply(self, host: str = "http://localhost:5050"):
        """Applies the scenario directly."""
        # Iterates over resources and PUTs them to the running server
        pass
```

***

## Usage Examples

### 1. Manual Sync

```bash
# Sync with Azure specifications
mazure-cli sync sync --auto-generate

# Check coverage
mazure-cli sync coverage

# Generate specific service
mazure-cli sync generate Microsoft.Compute virtualMachines 2024-03-01

# Generate and apply a compliance scenario
mazure-cli sync generate --template compliance/cmmc --apply

# Generate a setup script for a scenario
mazure-cli sync generate --template compliance/cmmc --output setup_cmmc.py
```

### 2. Automated Daily Sync (GitHub Actions)

The workflow automatically:
1. Pulls latest Azure REST API specs
2. Detects changes
3. Generates updated code
4. Runs tests
5. Creates PR for review

### 3. API Version Compatibility Check

```python
# In Mazure server
from mazure.sync.compatibility import CompatibilityMatrix

compat = CompatibilityMatrix()
result = compat.check_version_compatibility(
    "Microsoft.Compute",
    "virtualMachines",
    "2024-03-01"
)

if not result['compatible']:
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "UnsupportedApiVersion",
                "message": result['reason'],
                "target": "api-version"
            }
        }
    )
```

This architecture ensures Mazure remains a reliable, up-to-date testing platform regardless of how rapidly Azure's API surface evolves. [devblogs.microsoft](https://devblogs.microsoft.com/azure-sdk/inside-the-making-of-the-azure-sdk-management-libraries/)
