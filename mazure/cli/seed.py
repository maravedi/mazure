"""CLI commands for seeding mazure state from Azure discovery."""

import typer
import os
import asyncio
from typing import List, Optional
from pathlib import Path

app = typer.Typer(help="Seed mazure state from live Azure environments")


@app.command(name="from-azure")
def from_azure(
    tenant_id: str = typer.Argument(..., help="Azure tenant ID"),
    subscription: List[str] = typer.Option([], "--subscription", "-s", help="Subscription IDs to discover (leave empty for all)"),
    include_entra: bool = typer.Option(True, help="Include Entra ID objects (users, groups, apps)"),
    include_relationships: bool = typer.Option(True, help="Include resource relationships"),
    output_snapshot: Optional[Path] = typer.Option(None, "--output", "-o", help="Save snapshot to file for later use"),
    environment: str = typer.Option("AZURE_PUBLIC", "--environment", "-e", help="Azure environment (AZURE_PUBLIC, AZURE_GOVERNMENT, etc.)")
):
    """Seed mazure state from live Azure environment.
    
    This command uses AzureDiscovery to enumerate your Azure tenant and
    populates mazure's mock state with real resource topology.
    
    Examples:
        # Seed from entire tenant
        mazure seed from-azure <tenant-id>
        
        # Seed specific subscriptions only
        mazure seed from-azure <tenant-id> -s <sub-1> -s <sub-2>
        
        # Export snapshot for later use
        mazure seed from-azure <tenant-id> --output fixtures/prod.json
    
    Requires: Azure credentials configured (az login, service principal, etc.)
    """
    try:
        from azure_discovery import AzureDiscoveryRequest, AzureEnvironment
        from azure.identity.aio import DefaultAzureCredential
        from ..seeding.discovery_importer import DiscoveryStateSeeder
        from ..core.state import StateManager
    except ImportError as e:
        typer.echo(f"Error: Missing required package: {e}", err=True)
        typer.echo("\nInstall with: pip install azure-discovery azure-identity", err=True)
        raise typer.Exit(1)
    
    # Parse environment
    try:
        env = AzureEnvironment[environment]
    except KeyError:
        typer.echo(f"Error: Invalid environment '{environment}'", err=True)
        typer.echo(f"Valid options: {', '.join(e.name for e in AzureEnvironment)}", err=True)
        raise typer.Exit(1)
    
    async def run_seed():
        # Create discovery request
        request = AzureDiscoveryRequest(
            tenant_id=tenant_id,
            environment=env,
            subscriptions=subscription if subscription else [],
            include_entra=include_entra,
            include_relationships=include_relationships
        )
        
        # Get Azure credentials
        credential = DefaultAzureCredential()
        
        # Run discovery and seed state
        seeder = DiscoveryStateSeeder(StateManager())
        
        typer.echo("\n🔍 Starting Azure discovery...")
        stats = await seeder.seed_from_discovery(request)
        
        # Export snapshot if requested
        if output_snapshot:
            typer.echo(f"\n💾 Exporting snapshot to {output_snapshot}...")
            # Re-run discovery to get nodes/relationships for export
            from azure_discovery import run_discovery
            response = await run_discovery(request, credential)
            await seeder.export_snapshot(
                str(output_snapshot),
                response.nodes,
                response.relationships,
                metadata={
                    'tenant_id': tenant_id,
                    'subscriptions': subscription,
                    'environment': environment
                }
            )
        
        typer.echo("\n✅ Seeding complete!")
        typer.echo(f"  ARM Resources: {stats['arm_resources']}")
        typer.echo(f"  Entra Objects: {stats['entra_objects']}")
        typer.echo(f"  Relationships: {stats['relationships']}")
        
        await credential.close()
    
    # Run async function
    asyncio.run(run_seed())


if __name__ == "__main__":
    app()
