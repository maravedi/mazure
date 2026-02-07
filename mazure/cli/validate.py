"""CLI commands for discovery-based validation."""

import click
import asyncio
import json
from pathlib import Path
import logging

from ..sync.discovery_validator import DiscoveryBasedValidator
from ..codegen.schema_generator import SchemaGenerator
from ..scenarios.snapshot_manager import SnapshotManager

logger = logging.getLogger(__name__)


@click.group()
def validate():
    """Validation commands."""
    pass


@validate.command('service')
@click.argument('snapshot_file', type=click.Path(exists=True))
@click.option('--resource-type', '-t', help='Specific resource type to validate')
@click.option('--output', '-o', type=click.Path(), help='Output report file')
def validate_service(snapshot_file, resource_type, output):
    """Validate mock service against discovery snapshot.
    
    Examples:
        mazure validate service fixtures/prod.json
        mazure validate service fixtures/prod.json -t Microsoft.Compute/virtualMachines
        mazure validate service fixtures/prod.json -o validation-report.txt
    """
    async def run():
        # Load snapshot
        click.echo(f"Loading snapshot: {snapshot_file}")
        manager = SnapshotManager()
        nodes, _ = await manager.load_snapshot(Path(snapshot_file))
        
        # Convert nodes to dictionaries
        samples = []
        for node in nodes:
            samples.append({
                'type': node.type,
                'name': node.name,
                'location': node.location,
                'properties': node.properties,
                'tags': node.tags
            })
        
        # Initialize validator
        validator = DiscoveryBasedValidator(samples)
        
        # Validate
        if resource_type:
            click.echo(f"\nValidating: {resource_type}")
            # TODO: Get mock responses from service
            # For now, just analyze
            click.echo("Note: Mock response comparison not yet implemented")
            click.echo("This will compare your mock service responses with discovery data")
        else:
            click.echo("\nAnalyzing all resource types...")
        
        # Generate report
        report = validator.generate_report()
        
        if output:
            with open(output, 'w') as f:
                f.write(report)
            click.echo(f"\n✓ Report saved to: {output}")
        else:
            click.echo("\n" + report)
    
    asyncio.run(run())


@validate.command('schema')
@click.argument('snapshot_file', type=click.Path(exists=True))
@click.argument('resource_type')
@click.option('--export', '-e', type=click.Path(), help='Export Pydantic model to file')
def validate_schema(snapshot_file, resource_type, export):
    """Generate and validate schema for resource type.
    
    Examples:
        mazure validate schema fixtures/prod.json Microsoft.Compute/virtualMachines
        mazure validate schema fixtures/prod.json Microsoft.Network/virtualNetworks -e schemas/vnet.py
    """
    async def run():
        click.echo(f"Loading snapshot: {snapshot_file}")
        manager = SnapshotManager()
        nodes, _ = await manager.load_snapshot(Path(snapshot_file))
        
        # Convert to dicts
        samples = []
        for node in nodes:
            if node.type.lower() == resource_type.lower():
                samples.append({
                    'type': node.type,
                    'properties': node.properties
                })
        
        if not samples:
            click.echo(f"❌ No samples found for {resource_type}")
            return
        
        click.echo(f"Found {len(samples)} samples")
        
        # Generate schema
        generator = SchemaGenerator(samples)
        schema = generator.analyze_resources(resource_type)
        
        # Display coverage
        click.echo(f"\n✓ Schema Analysis:")
        click.echo(f"  Total properties: {len(schema['properties'])}")
        click.echo(f"  Required: {len(schema['required_fields'])}")
        click.echo(f"  Optional: {len(schema['optional_fields'])}")
        
        # Generate Pydantic model
        model_code = generator.generate_pydantic_model(resource_type)
        
        if export:
            with open(export, 'w') as f:
                f.write(model_code)
            click.echo(f"\n✓ Pydantic model exported to: {export}")
        else:
            click.echo(f"\n{model_code}")
        
        # Coverage report
        report = generator.get_coverage_report()
        click.echo(f"\nCoverage Report:")
        click.echo(json.dumps(report, indent=2))
    
    asyncio.run(run())
