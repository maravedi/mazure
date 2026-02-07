"""Schema generator for creating Pydantic models from discovery data.

Analyzes discovered resources to automatically generate type-safe schemas.
"""

from typing import Type, List, Dict, Any, get_type_hints, Optional
from collections import defaultdict, Counter
import logging
from pathlib import Path

try:
    from pydantic import BaseModel, create_model, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    logger.warning("Pydantic not available. Schema generation will be limited.")

logger = logging.getLogger(__name__)


class SchemaGenerator:
    """Generate Pydantic schemas from discovery models.
    
    Analyzes discovered resource samples to infer schema structure,
    field types, and nullability.
    """
    
    def __init__(self):
        """Initialize schema generator."""
        if not PYDANTIC_AVAILABLE:
            raise ImportError("Pydantic is required for schema generation")
    
    def generate_resource_schema(
        self,
        resource_type: str,
        sample_nodes: List[Any],
        min_coverage: float = 0.5
    ) -> Type[BaseModel]:
        """Infer Pydantic schema from discovered resource samples.
        
        Args:
            resource_type: Azure resource type (e.g., 'Microsoft.Compute/virtualMachines')
            sample_nodes: List of ResourceNode samples from discovery
            min_coverage: Minimum percentage of samples that must contain a field
        
        Returns:
            Dynamically generated Pydantic model class
        """
        if not sample_nodes:
            raise ValueError(f"No samples provided for {resource_type}")
        
        # Aggregate property statistics from samples
        property_stats = defaultdict(lambda: {'types': [], 'values': [], 'count': 0})
        
        for node in sample_nodes:
            if node.type == resource_type:
                props = getattr(node, 'properties', None) or {}
                for key, value in props.items():
                    property_stats[key]['types'].append(type(value))
                    property_stats[key]['values'].append(value)
                    property_stats[key]['count'] += 1
        
        # Build field definitions
        fields = {}
        for prop_name, stats in property_stats.items():
            # Include field if it appears in min_coverage% of samples
            coverage = stats['count'] / len(sample_nodes)
            if coverage >= min_coverage:
                field_type = self._infer_type(stats['types'], stats['values'])
                
                # Make optional if not present in all samples
                if coverage < 1.0:
                    field_type = Optional[field_type]
                    fields[prop_name] = (field_type, Field(default=None))
                else:
                    fields[prop_name] = (field_type, Field(...))
        
        # Generate dynamic Pydantic model
        schema_name = self._generate_schema_name(resource_type)
        return create_model(schema_name, **fields)
    
    def _generate_schema_name(self, resource_type: str) -> str:
        """Generate valid Python class name from resource type.
        
        Args:
            resource_type: Azure resource type
        
        Returns:
            Valid class name
        """
        # Convert Microsoft.Compute/virtualMachines -> MicrosoftComputeVirtualMachinesProperties
        name = resource_type.replace('/', '_').replace('.', '_').replace('-', '_')
        # Title case each part
        parts = name.split('_')
        name = ''.join(p.capitalize() for p in parts if p)
        return f"{name}Properties"
    
    def _infer_type(self, type_samples: List[type], value_samples: List[Any]) -> type:
        """Infer Python type from sample values.
        
        Handles type conflicts by choosing most specific common type.
        
        Args:
            type_samples: List of types observed
            value_samples: List of actual values
        
        Returns:
            Python type annotation
        """
        # Filter out None values
        non_none_types = [t for t, v in zip(type_samples, value_samples) if v is not None]
        
        if not non_none_types:
            return Any
        
        type_counts = Counter(non_none_types)
        most_common_type = type_counts.most_common(1)[0][0]
        
        # Type mapping
        if most_common_type == bool:
            return bool
        elif most_common_type == int:
            # Could be int or float if mixed
            if float in type_counts:
                return float
            return int
        elif most_common_type == float:
            return float
        elif most_common_type == list:
            # Try to infer list element type
            list_elements = [item for v in value_samples if isinstance(v, list) for item in v]
            if list_elements:
                element_type = self._infer_type(
                    [type(e) for e in list_elements],
                    list_elements
                )
                return List[element_type]
            return List[Any]
        elif most_common_type == dict:
            return Dict[str, Any]
        else:
            return str
    
    def generate_all_schemas(
        self,
        nodes: List[Any],
        output_dir: Path,
        min_samples: int = 3
    ) -> Dict[str, Type[BaseModel]]:
        """Generate schema modules for all discovered resource types.
        
        Args:
            nodes: List of ResourceNode objects
            output_dir: Directory to write schema modules
            min_samples: Minimum samples required to generate schema
        
        Returns:
            Dict mapping resource type to generated schema class
        """
        # Group nodes by type
        by_type = defaultdict(list)
        for node in nodes:
            # Skip Entra ID graph resources
            if hasattr(node, 'id') and not str(node.id).startswith('graph://'):
                by_type[node.type].append(node)
        
        generated_schemas = {}
        
        # Generate schema for each type
        for resource_type, samples in by_type.items():
            if len(samples) < min_samples:
                logger.debug(f"Skipping {resource_type}: only {len(samples)} samples (need {min_samples})")
                continue
            
            try:
                schema = self.generate_resource_schema(resource_type, samples)
                generated_schemas[resource_type] = schema
                
                # Write to module
                provider = resource_type.split('/')[0].replace('.', '_').lower()
                module_path = output_dir / f"{provider}_schemas.py"
                
                self._write_schema_module(module_path, resource_type, schema)
                
                logger.info(f"Generated schema for {resource_type} ({len(samples)} samples)")
                
            except Exception as e:
                logger.error(f"Failed to generate schema for {resource_type}: {str(e)}")
        
        return generated_schemas
    
    def _write_schema_module(self, path: Path, resource_type: str, schema: Type[BaseModel]):
        """Write Pydantic schema to Python module.
        
        Args:
            path: Path to module file
            resource_type: Azure resource type
            schema: Generated Pydantic model
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists to append or create
        mode = 'a' if path.exists() else 'w'
        
        with open(path, mode) as f:
            if mode == 'w':
                # Write header for new file
                f.write('"""Auto-generated schemas from Azure Discovery data."""\n\n')
                f.write('from typing import Optional, List, Dict, Any\n')
                f.write('from pydantic import BaseModel, Field\n\n')
            
            # Write schema class
            f.write(f"\n# {resource_type}\n")
            f.write(f"class {schema.__name__}(BaseModel):\n")
            f.write(f'    """Properties for {resource_type}."""\n\n')
            
            if not schema.__fields__:
                f.write('    pass\n')
            else:
                for field_name, field_info in schema.__fields__.items():
                    # Get type annotation as string
                    annotation = field_info.annotation
                    type_str = self._type_to_string(annotation)
                    
                    # Check if field has default
                    if field_info.default is None:
                        f.write(f"    {field_name}: {type_str} = None\n")
                    elif field_info.is_required():
                        f.write(f"    {field_name}: {type_str}\n")
                    else:
                        f.write(f"    {field_name}: {type_str} = Field(default=None)\n")
            
            f.write('\n')
    
    def _type_to_string(self, annotation) -> str:
        """Convert type annotation to string representation.
        
        Args:
            annotation: Type annotation
        
        Returns:
            String representation
        """
        # Handle Optional types
        if hasattr(annotation, '__origin__'):
            origin = annotation.__origin__
            
            if origin is type(Optional[int]):
                # Optional[X] -> Optional[X]
                args = annotation.__args__
                inner = self._type_to_string(args[0]) if args else 'Any'
                return f"Optional[{inner}]"
            
            elif origin is list:
                args = annotation.__args__
                inner = self._type_to_string(args[0]) if args else 'Any'
                return f"List[{inner}]"
            
            elif origin is dict:
                return "Dict[str, Any]"
        
        # Simple types
        if annotation == str:
            return "str"
        elif annotation == int:
            return "int"
        elif annotation == float:
            return "float"
        elif annotation == bool:
            return "bool"
        elif annotation == Any:
            return "Any"
        
        # Fallback
        return str(annotation).replace('typing.', '')
    
    def export_schema_summary(self, schemas: Dict[str, Type[BaseModel]], output_path: Path):
        """Export summary of generated schemas.
        
        Args:
            schemas: Dict of resource type to schema
            output_path: Path to write summary JSON
        """
        import json
        
        summary = {
            'total_schemas': len(schemas),
            'schemas': {}
        }
        
        for resource_type, schema in schemas.items():
            summary['schemas'][resource_type] = {
                'class_name': schema.__name__,
                'field_count': len(schema.__fields__),
                'fields': {
                    name: {
                        'type': self._type_to_string(field.annotation),
                        'required': field.is_required()
                    }
                    for name, field in schema.__fields__.items()
                }
            }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Exported schema summary to {output_path}")


class SchemaGeneratorFactory:
    """Factory for creating SchemaGenerator and generating from various sources."""
    
    @staticmethod
    def from_snapshot(
        snapshot_path: str,
        output_dir: str,
        min_samples: int = 3
    ) -> Dict[str, Type[BaseModel]]:
        """Generate schemas from snapshot file.
        
        Args:
            snapshot_path: Path to snapshot JSON
            output_dir: Directory for generated schemas
            min_samples: Minimum samples per type
        
        Returns:
            Dict of generated schemas
        """
        from pathlib import Path
        from ..scenarios.snapshot_manager import SnapshotManager
        
        # Load snapshot
        manager = SnapshotManager()
        nodes, _ = manager.load_snapshot(Path(snapshot_path))
        
        # Generate schemas
        generator = SchemaGenerator()
        schemas = generator.generate_all_schemas(
            nodes,
            Path(output_dir),
            min_samples=min_samples
        )
        
        # Export summary
        summary_path = Path(output_dir) / 'schema_summary.json'
        generator.export_schema_summary(schemas, summary_path)
        
        return schemas
