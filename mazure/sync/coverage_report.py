import argparse
import asyncio
from pathlib import Path
from mazure.sync.spec_sync import AzureSpecSyncEngine

async def main():
    parser = argparse.ArgumentParser(description="Generate API coverage report")
    parser.add_argument("--output", type=Path, required=True, help="Output Markdown report")

    args = parser.parse_args()

    engine = AzureSpecSyncEngine(
        specs_repo_path=Path("specs/azure-rest-api-specs"),
        mazure_root=Path.cwd()
    )

    await engine.initialize()

    coverage = await engine.get_service_coverage()

    # Generate Markdown
    md = f"""# Mazure API Coverage Report

**Date:** {coverage['timestamp']}

## Summary
- **Total Azure Providers:** {coverage['total_providers']}
- **Implemented in Mazure:** {coverage['implemented_providers']}
- **Coverage:** {coverage['coverage_percentage']}%

## Implemented Providers
"""

    for provider in coverage['providers']['implemented']:
        md += f"- {provider}\n"

    md += "\n## Missing Providers (Top 20)\n"
    for provider in coverage['providers']['missing'][:20]:
        md += f"- {provider}\n"

    with open(args.output, "w") as f:
        f.write(md)

    print(f"Coverage report saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
