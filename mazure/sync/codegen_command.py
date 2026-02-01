import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from mazure.sync.codegen import MazureCodeGenerator

async def process_pending_tasks(
    tasks_file: Path,
    specs_path: Path,
    mazure_root: Path,
    dry_run: bool = False
):
    if not tasks_file.exists():
        print(f"Tasks file {tasks_file} not found. Exiting.")
        return

    with open(tasks_file) as f:
        tasks = json.load(f)

    if not tasks:
        print("No pending tasks.")
        return

    # Filter pending tasks
    pending_tasks = [t for t in tasks if t.get('status') == 'pending']

    if not pending_tasks:
        print("No pending tasks to process.")
        return

    print(f"Found {len(pending_tasks)} pending tasks.")

    if dry_run:
        print("Auto-approve is not enabled. Skipping generation.")
        return

    generator = MazureCodeGenerator(
        specs_path=specs_path,
        mazure_root=mazure_root
    )

    for task in pending_tasks:
        print(f"Generating {task['provider']}/{task['resource_type']} (v{task['api_version']})...")

        full_spec_path = specs_path / task['spec_path']

        try:
            await generator.generate_service(
                provider=task['provider'],
                resource_type=task['resource_type'],
                api_version=task['api_version'],
                spec_path=full_spec_path
            )
            task['status'] = 'completed'
            task['generated_at'] = datetime.utcnow().isoformat()

        except Exception as e:
            print(f"Error generating {task['id']}: {e}")
            task['status'] = 'failed'
            task['error'] = str(e)

    # Update tasks file
    with open(tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)

async def main():
    parser = argparse.ArgumentParser(description="Generate code from pending updates")
    parser.add_argument("--tasks-file", type=Path, required=True, help="Path to pending_updates.json")
    parser.add_argument("--specs-path", type=Path, required=True, help="Path to azure-rest-api-specs")
    parser.add_argument("--auto-approve", type=str, default="false", help="Auto approve generation")

    args = parser.parse_args()

    dry_run = args.auto_approve.lower() != "true"

    await process_pending_tasks(
        tasks_file=args.tasks_file,
        specs_path=args.specs_path,
        mazure_root=Path.cwd(),
        dry_run=dry_run
    )

if __name__ == "__main__":
    asyncio.run(main())
