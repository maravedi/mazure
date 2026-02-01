import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from enum import Enum
from mazure.sync.spec_sync import AzureSpecSyncEngine

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

async def main():
    parser = argparse.ArgumentParser(description="Sync with Azure API specifications")
    parser.add_argument("--specs-path", type=Path, required=True, help="Path to azure-rest-api-specs")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON report")
    parser.add_argument("--update-tasks", type=Path, help="Path to update pending tasks file")

    args = parser.parse_args()

    engine = AzureSpecSyncEngine(
        specs_repo_path=args.specs_path,
        mazure_root=Path.cwd(),
        tasks_file_path=args.update_tasks
    )

    changes = await engine.sync()

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "changes_count": len(changes),
        "changes": [
            {
                "change_type": c.change_type.value,
                "provider": c.provider,
                "resource_type": c.resource_type,
                "api_version": c.api_version,
                "spec_path": str(c.spec_path),
                "details": c.details,
                "timestamp": c.timestamp.isoformat()
            }
            for c in changes
        ]
    }

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, cls=DateTimeEncoder)

    print(f"Sync complete. Found {len(changes)} changes. Report saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
