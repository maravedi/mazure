import json
import os
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any

class ScenarioGenerator:
    def __init__(self, template_name: str, mazure_root: Path):
        self.mazure_root = mazure_root
        self.template_name = template_name
        self.template_path = self._find_template(template_name)
        self.data = self._load_template()

    def _find_template(self, name: str) -> Path:
        """Finds the template JSON file."""
        # Try direct path first
        p = Path(name)
        if p.exists() and p.suffix == '.json':
            return p

        # Look in templates dir
        templates_dir = self.mazure_root / "mazure" / "scenarios" / "templates"

        # Check name as is (e.g. compliance/cmmc)
        p = templates_dir / f"{name}.json"
        if p.exists():
            return p

        # Check if name has extension
        p = templates_dir / name
        if p.exists():
            return p

        raise FileNotFoundError(f"Template '{name}' not found in {templates_dir}")

    def _load_template(self) -> List[Dict[str, Any]]:
        with open(self.template_path, 'r') as f:
            return json.load(f)

    def generate_script(self, output_path: Optional[Path] = None) -> Path:
        """Generates a Python script to apply the scenario."""
        if output_path is None:
            safe_name = self.template_name.replace('/', '_').replace('\\', '_').replace('.', '_')
            output_path = Path(f"setup_{safe_name}.py")

        script_content = self._build_script_content()

        with open(output_path, 'w') as f:
            f.write(script_content)

        return output_path

    def _build_script_content(self) -> str:
        resources_json = json.dumps(self.data, indent=4)

        return f"""#!/usr/bin/env python3
import requests
import json
import sys
import time

def setup_scenario(host="http://localhost:5050"):
    print(f"Applying scenario to {{host}}...")

    resources = {resources_json}

    for r in resources:
        # Construct URL
        # /subscriptions/{{sub}}/resourceGroups/{{rg}}/providers/{{provider}}/{{type}}/{{name}}

        subscription_id = r.get('subscription_id', '00000000-0000-0000-0000-000000000000')
        resource_group = r.get('resource_group', 'default-rg')
        provider = r.get('provider')
        resource_type = r.get('resource_type')
        name = r.get('name')
        api_version = r.get('api_version', '2021-01-01')
        properties = r.get('properties', {{}})

        if not all([provider, resource_type, name]):
            print(f"Skipping invalid resource entry: {{r}}")
            continue

        if provider == 'Microsoft.Resources' and resource_type == 'resourceGroups':
            url = f"{{host}}/subscriptions/{{subscription_id}}/resourceGroups/{{name}}"
        else:
            url = f"{{host}}/subscriptions/{{subscription_id}}/resourceGroups/{{resource_group}}/providers/{{provider}}/{{resource_type}}/{{name}}"
        params = {{'api-version': api_version}}

        print(f"Creating {{provider}}/{{resource_type}}/{{name}}...")
        try:
            # Azure usually uses PUT for creation
            resp = requests.put(url, json=properties, params=params)
            if resp.status_code in [200, 201]:
                print(f"  -> Success")
            else:
                print(f"  -> Failed ({{resp.status_code}}): {{resp.text}}")
        except Exception as e:
            print(f"  -> Error: {{e}}")

if __name__ == "__main__":
    host = "http://localhost:5050"
    if len(sys.argv) > 1:
        host = sys.argv[1]
    setup_scenario(host)
"""

    def apply(self, host: str = "http://localhost:5050"):
        """Applies the scenario directly."""
        print(f"[scenario] Applying template '{self.template_name}' to {host}...")

        for r in self.data:
            subscription_id = r.get('subscription_id', '00000000-0000-0000-0000-000000000000')
            resource_group = r.get('resource_group', 'default-rg')
            provider = r.get('provider')
            resource_type = r.get('resource_type')
            name = r.get('name')
            api_version = r.get('api_version', '2021-01-01')
            properties = r.get('properties', {})

            if not all([provider, resource_type, name]):
                print(f"Skipping invalid resource entry: {r}")
                continue

            if provider == 'Microsoft.Resources' and resource_type == 'resourceGroups':
                url = f"{host}/subscriptions/{subscription_id}/resourceGroups/{name}"
            else:
                url = f"{host}/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{provider}/{resource_type}/{name}"
            params = {'api-version': api_version}

            # print(f"PUT {url}")
            try:
                resp = requests.put(url, json=properties, params=params)
                if resp.status_code in [200, 201]:
                    print(f"  ✓ {name}")
                else:
                    print(f"  ✗ {name} - {resp.status_code}: {resp.text}")
            except requests.exceptions.ConnectionError:
                 print(f"  ! Connection failed. Is Mazure server running at {host}?")
                 break
            except Exception as e:
                print(f"  ! Error applying {name}: {e}")
