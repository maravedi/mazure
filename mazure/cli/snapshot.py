"""CLI commands for managing discovery snapshots."""

import typer
import asyncio
from pathlib import Path
from typing import Optional

app = typer.Typer(help="Manage discovery snapshot fixtures")


@app.command()
def load(
    snapshot_path: Path = typer.Argument(..., help="Path to snapshot JSON file"),
    clear: bool = typer.Option(False, "--clear", help="Clear existing state before loading")
):
    """Load snapshot into mazure mock state.
    
    Populates mazure with resources and relationships from a saved snapshot.
    Useful for setting up deterministic test environments.
    
    Examples:
        # Load snapshot into current state
        mazure snapshot load fixtures/prod.json
        
        # Clear state and load snapshot
        mazure snapshot load fixtures/prod.json --clear
    """
    try:
        from ..scenarios.snapshot_manager import SnapshotManager
        from ..core.state import StateManager
    except ImportError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    if not snapshot_path.exists():
        typer.echo(f"Error: Snapshot not found: {snapshot_path}", err=True)
        raise typer.Exit(1)
    
    async def run_load():
        manager = SnapshotManager()
        await manager.seed_from_snapshot(
            snapshot_path,
            StateManager(),
            clear_existing=clear
        )
        
        typer.echo(f"\n✅ Snapshot loaded from {snapshot_path}")
    
    asyncio.run(run_load())


@app.command()
def list_cmd(
    fixtures_dir: Path = typer.Option(
        Path('fixtures'),
        "--dir", "-d",
        help="Fixtures directory to scan"
    )
):
    """List available snapshot fixtures.
    
    Scans a directory for snapshot JSON files and displays their metadata.
    
    Examples:
        # List snapshots in default fixtures/ directory
        mazure snapshot list
        
        # List snapshots in custom directory
        mazure snapshot list --dir /path/to/fixtures
    """
    try:
        from ..scenarios.snapshot_manager import SnapshotManager
    except ImportError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    
    manager = SnapshotManager()
    snapshots = manager.list_snapshots(fixtures_dir)
    
    if not snapshots:
        typer.echo(f"No snapshots found in {fixtures_dir}")
        return
    
    typer.echo(f"\n📸 Found {len(snapshots)} snapshot(s) in {fixtures_dir}:\n")
    
    for snap in snapshots:
        meta = snap['metadata']
        typer.echo(f"  {snap['path']}")
        typer.echo(f"    Created: {meta.get('created_at', 'unknown')}")
        typer.echo(f"    Nodes: {meta.get('node_count', 0)}")
        typer.echo(f"    Relationships: {meta.get('relationship_count', 0)}")
        
        if 'tenant_id' in meta:
            typer.echo(f"    Tenant: {meta['tenant_id']}")
        if 'subscriptions' in meta and meta['subscriptions']:
            typer.echo(f"    Subscriptions: {', '.join(meta['subscriptions'])}")
        
        typer.echo()


# Alias for better UX
app.command(name="list")(list_cmd)


if __name__ == "__main__":
    app()
