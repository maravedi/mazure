"""Dynamic Pydantic schema generation from discovery samples."""

from typing import Dict, Any, List, Set, Optional, Type
from collections import defaultdict, Counter
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SchemaGenerator:
    """Generate Pydantic models from discovered Azure resources.
    
    Analyzes historical discovery data to infer property types,
    nullability, and generate accurate Pydantic schemas.
    """
    
    def __init__(self, samples: List[Dict[str, Any]]):
        """Initialize with resource samples.
        
        Args:
            samples: List of resource dictionaries from discovery
        """
        self.samples = samples
        self.schemas = {}
        self.type_stats = defaultdict(lambda: defaultdict(lambda: {
            'types': Counter(),
            'null_count': 0,
            'sample_values': []
        }))
    
    def analyze_resources(self, resource_type: str) -> Dict[str, Any]:
        """Analyze samples for a specific resource type.
        
        Args:
            resource_type: Azure resource type to analyze
        
        Returns:
            Schema dictionary with field information
        """
        type_samples = [
            s for s in self.samples 
            if s.get('type', '').lower() == resource_type.lower()
        ]
        
        if not type_samples:
            logger.warning(f"No samples found for {resource_type}")
            return {}
        
        logger.info(f"Analyzing {len(type_samples)} samples of {resource_type}")
        
        schema = {
            'resource_type': resource_type,
            'sample_count': len(type_samples),
            'properties': {},
            'required_fields': set(),
            'optional_fields': set()
        }
        
        # Analyze properties
        property_data = defaultdict(lambda: {
            'types': Counter(),
            'null_count': 0,
            'non_null_count': 0,
            'sample_values': []
        })
        
        for sample in type_samples:
            properties = sample.get('properties', {})
            if not isinstance(properties, dict):
                continue
            
            # Track which properties appear
            seen_props = set(properties.keys())
            
            for key, value in properties.items():
                if value is None:
                    property_data[key]['null_count'] += 1
                else:
                    property_data[key]['non_null_count'] += 1
                    property_data[key]['types'][type(value).__name__] += 1
                    
                    # Store sample values (up to 5)
                    if len(property_data[key]['sample_values']) < 5:
                        property_data[key]['sample_values'].append(value)
        
        # Generate schema for each property
        for prop_name, data in property_data.items():
            total_appearances = data['null_count'] + data['non_null_count']
            null_percentage = (data['null_count'] / total_appearances * 100) if total_appearances > 0 else 0
            
            # Determine primary type
            if data['types']:
                primary_type = data['types'].most_common(1)[0][0]
            else:
                primary_type = 'NoneType'
            
            # Determine if required (appears in >80% and rarely null)
            is_required = (total_appearances >= len(type_samples) * 0.8 and null_percentage < 10)
            
            schema['properties'][prop_name] = {
                'python_type': primary_type,
                'nullable': null_percentage > 0,
                'null_percentage': round(null_percentage, 2),
                'appearances': total_appearances,
                'coverage': round(total_appearances / len(type_samples) * 100, 2),
                'sample_values': data['sample_values'][:3]
            }
            
            if is_required:
                schema['required_fields'].add(prop_name)
            else:
                schema['optional_fields'].add(prop_name)
        
        # Convert sets to lists for JSON serialization
        schema['required_fields'] = sorted(list(schema['required_fields']))
        schema['optional_fields'] = sorted(list(schema['optional_fields']))
        
        self.schemas[resource_type] = schema
        return schema
    
    def generate_pydantic_model(self, resource_type: str) -> str:
        """Generate Pydantic model code for a resource type.
        
        Args:
            resource_type: Azure resource type
        
        Returns:
            Python code string for Pydantic model
        """
        if resource_type not in self.schemas:
            self.analyze_resources(resource_type)
        
        schema = self.schemas.get(resource_type)
        if not schema:
            return f"# No schema available for {resource_type}"
        
        # Generate class name from resource type
        class_name = self._resource_type_to_class_name(resource_type)
        
        # Build model code
        lines = [
            'from pydantic import BaseModel, Field',
            'from typing import Optional, Any, List, Dict',
            'from datetime import datetime',
            '',
            '',
            f'class {class_name}Properties(BaseModel):',
            f'    """Properties for {resource_type}."""',
            ''
        ]
        
        # Add fields
        for prop_name, prop_info in sorted(schema['properties'].items()):
            field_name = self._sanitize_field_name(prop_name)
            python_type = self._python_type_to_annotation(prop_info['python_type'])
            
            # Make optional if nullable or not required
            if prop_info['nullable'] or prop_name in schema['optional_fields']:
                type_annotation = f"Optional[{python_type}]"
                default = " = None"
            else:
                type_annotation = python_type
                default = ""
            
            # Add docstring as comment
            coverage = prop_info['coverage']
            lines.append(f"    {field_name}: {type_annotation}{default}  # Coverage: {coverage}%")
        
        return '\n'.join(lines)
    
    def export_schemas(self, output_file: str):
        """Export all generated schemas to a Python module.
        
        Args:
            output_file: Path to output .py file
        """
        with open(output_file, 'w') as f:
            f.write('"""Auto-generated Pydantic schemas from Azure discovery."""\n\n')
            f.write('# Generated: {}\n'.format(datetime.now().isoformat()))
            f.write('# WARNING: This file is auto-generated. Do not edit manually.\n\n')
            
            for resource_type in sorted(self.schemas.keys()):
                model_code = self.generate_pydantic_model(resource_type)
                f.write(model_code)
                f.write('\n\n\n')
        
        logger.info(f"Exported {len(self.schemas)} schemas to {output_file}")
    
    def get_coverage_report(self) -> Dict[str, Any]:
        """Get coverage statistics for all analyzed schemas.
        
        Returns:
            Dictionary with coverage statistics
        """
        report = {
            'total_types': len(self.schemas),
            'types': {}
        }
        
        for resource_type, schema in self.schemas.items():
            report['types'][resource_type] = {
                'sample_count': schema['sample_count'],
                'total_properties': len(schema['properties']),
                'required_properties': len(schema['required_fields']),
                'optional_properties': len(schema['optional_fields']),
                'avg_coverage': round(
                    sum(p['coverage'] for p in schema['properties'].values()) / 
                    len(schema['properties']) if schema['properties'] else 0,
                    2
                )
            }
        
        return report
    
    @staticmethod
    def _resource_type_to_class_name(resource_type: str) -> str:
        """Convert resource type to Python class name.
        
        Args:
            resource_type: Azure resource type (e.g., 'Microsoft.Compute/virtualMachines')
        
        Returns:
            Python class name (e.g., 'VirtualMachine')
        """
        # Extract the last part after /
        name = resource_type.split('/')[-1]
        # Convert to PascalCase
        parts = re.findall(r'[A-Z][a-z]*|[a-z]+', name)
        return ''.join(part.capitalize() for part in parts)
    
    @staticmethod
    def _sanitize_field_name(field_name: str) -> str:
        """Convert field name to valid Python identifier.
        
        Args:
            field_name: Original field name
        
        Returns:
            Valid Python identifier
        """
        # Replace invalid characters with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', field_name)
        # Ensure doesn't start with number
        if sanitized[0].isdigit():
            sanitized = 'field_' + sanitized
        return sanitized
    
    @staticmethod
    def _python_type_to_annotation(python_type: str) -> str:
        """Convert Python type name to type annotation.
        
        Args:
            python_type: Python type name (e.g., 'dict', 'list')
        
        Returns:
            Type annotation string
        """
        type_map = {
            'dict': 'Dict[str, Any]',
            'list': 'List[Any]',
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'NoneType': 'Any'
        }
        return type_map.get(python_type, 'Any')
