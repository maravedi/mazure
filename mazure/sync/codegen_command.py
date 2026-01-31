import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from mazure.sync.codegen import MazureCodeGenerator

async def main():
    parser = argparse.ArgumentParser(description="Generate code from pending updates")
    parser.add_argument("--tasks-file", type=Path, required=True, help="Path to pending_updates.json")
    parser.add_argument("--specs-path", type=Path, required=True, help="Path to azure-rest-api-specs")
    parser.add_argument("--auto-approve", type=str, default="false", help="Auto approve generation")

    args = parser.parse_args()

    if not args.tasks_file.exists():
        print(f"Tasks file {args.tasks_file} not found. Exiting.")
        return

    with open(args.tasks_file) as f:
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

    if args.auto_approve.lower() != "true":
        print("Auto-approve is not enabled. Skipping generation.")
        return

    specs_root = args.specs_path

    generator = MazureCodeGenerator(
        specs_path=specs_root,
        mazure_root=Path.cwd()
    )

    for task in pending_tasks:
        print(f"Generating {task['provider']}/{task['resource_type']} (v{task['api_version']})...")

        full_spec_path = specs_root / task['spec_path']

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
    with open(args.tasks_file, 'w') as f:
        json.dump(tasks, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
