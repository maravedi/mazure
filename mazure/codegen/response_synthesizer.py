"""Response synthesizer for generating realistic Azure resources.

Analyzes patterns from discovery data to generate statistically realistic
mock resources for testing.
"""

from collections import Counter, defaultdict
from typing import List, Dict, Any, Optional
import random
import logging

logger = logging.getLogger(__name__)


class ResponseSynthesizer:
    """Generate realistic responses based on discovery patterns.
    
    Analyzes historical discovery data to learn patterns and generate
    statistically realistic mock resources.
    """
    
    def __init__(self, historical_nodes: List[Any]):
        """Initialize with historical discovery data.
        
        Args:
            historical_nodes: List of ResourceNode objects from past discoveries
        """
        self.nodes = historical_nodes
        self.type_counts = Counter()
        self.location_distribution = {}
        self.tag_patterns = {}
        self.property_patterns = {}
        
        if historical_nodes:
            self._analyze_patterns()
            logger.info(f"Analyzed {len(historical_nodes)} resources across {len(self.type_counts)} types")
    
    def _analyze_patterns(self):
        """Analyze patterns in discovered resources."""
        # Resource type frequency
        self.type_counts = Counter(n.type for n in self.nodes)
        
        # Location distribution per type
        self.location_distribution = {}
        for node in self.nodes:
            if node.type not in self.location_distribution:
                self.location_distribution[node.type] = Counter()
            if hasattr(node, 'location') and node.location:
                self.location_distribution[node.type][node.location] += 1
        
        # Tag patterns
        self.tag_patterns = self._extract_tag_patterns()
        
        # Property patterns per type
        self.property_patterns = self._extract_property_patterns()
    
    def _extract_tag_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Extract common tag keys and value patterns per resource type.
        
        Returns:
            Dict mapping resource_type -> tag_key -> list of observed values
        """
        patterns = {}
        
        for node in self.nodes:
            if node.type not in patterns:
                patterns[node.type] = {}
            
            tags = getattr(node, 'tags', None) or {}
            for key, value in tags.items():
                if key.startswith('_'):  # Skip internal tags
                    continue
                if key not in patterns[node.type]:
                    patterns[node.type][key] = []
                if value and value not in patterns[node.type][key]:
                    patterns[node.type][key].append(str(value))
        
        return patterns
    
    def _extract_property_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Extract property patterns per resource type.
        
        Returns:
            Dict mapping resource_type -> property_key -> pattern info
        """
        patterns = {}
        
        for node in self.nodes:
            if node.type not in patterns:
                patterns[node.type] = {}
            
            props = getattr(node, 'properties', None) or {}
            for key, value in props.items():
                if key not in patterns[node.type]:
                    patterns[node.type][key] = {
                        'type': type(value).__name__,
                        'values': [],
                        'null_count': 0
                    }
                
                if value is None:
                    patterns[node.type][key]['null_count'] += 1
                else:
                    # Store sample values (up to 10 unique)
                    if len(patterns[node.type][key]['values']) < 10:
                        if value not in patterns[node.type][key]['values']:
                            patterns[node.type][key]['values'].append(value)
        
        return patterns
    
    def synthesize_resource(
        self,
        resource_type: str,
        name: Optional[str] = None,
        location: Optional[str] = None,
        override_properties: Optional[Dict[str, Any]] = None,
        override_tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate realistic resource based on observed patterns.
        
        Args:
            resource_type: Azure resource type (e.g., 'Microsoft.Compute/virtualMachines')
            name: Resource name (auto-generated if not provided)
            location: Azure region (selected based on distribution if not provided)
            override_properties: Explicit property values to use
            override_tags: Explicit tag values to use
        
        Returns:
            Dict representing a realistic ARM resource
        """
        # Find similar resources as templates
        similar = [n for n in self.nodes if n.type == resource_type]
        
        if not similar:
            logger.warning(f"No examples found for {resource_type}. Generating minimal resource.")
            return self._generate_minimal_resource(resource_type, name, location)
        
        # Pick a template resource
        template = random.choice(similar)
        
        # Generate properties
        properties = {}
        if resource_type in self.property_patterns:
            for prop_key, pattern_info in self.property_patterns[resource_type].items():
                if pattern_info['values']:
                    # Use observed value
                    properties[prop_key] = random.choice(pattern_info['values'])
                elif pattern_info['type'] == 'str':
                    properties[prop_key] = f"mock-{prop_key}-{random.randint(1000, 9999)}"
                elif pattern_info['type'] == 'int':
                    properties[prop_key] = random.randint(1, 100)
                elif pattern_info['type'] == 'bool':
                    properties[prop_key] = random.choice([True, False])
                elif pattern_info['type'] == 'list':
                    properties[prop_key] = []
                elif pattern_info['type'] == 'dict':
                    properties[prop_key] = {}
        
        # Apply overrides
        if override_properties:
            properties.update(override_properties)
        
        # Pick realistic location
        if not location:
            if resource_type in self.location_distribution and self.location_distribution[resource_type]:
                locations = list(self.location_distribution[resource_type].keys())
                weights = list(self.location_distribution[resource_type].values())
                location = random.choices(locations, weights=weights, k=1)[0]
            else:
                location = 'eastus'  # Default fallback
        
        # Generate realistic tags
        tags = {}
        if resource_type in self.tag_patterns:
            for tag_key, values in self.tag_patterns[resource_type].items():
                if random.random() < 0.7:  # 70% chance to include each tag
                    tags[tag_key] = random.choice(values) if values else f"value-{tag_key}"
        
        # Apply tag overrides
        if override_tags:
            tags.update(override_tags)
        
        # Generate name if not provided
        if not name:
            template_name = getattr(template, 'name', 'resource')
            prefix = template_name.split('-')[0] if '-' in template_name else template_name[:3]
            name = f"{prefix}-{random.randint(1000, 9999)}"
        
        # Build resource ID
        resource_id = self._generate_resource_id(resource_type, name)
        
        return {
            'id': resource_id,
            'type': resource_type,
            'name': name,
            'location': location,
            'properties': properties,
            'tags': tags
        }
    
    def _generate_minimal_resource(
        self,
        resource_type: str,
        name: Optional[str],
        location: Optional[str]
    ) -> Dict[str, Any]:
        """Generate minimal resource when no templates available.
        
        Args:
            resource_type: Resource type
            name: Resource name
            location: Azure region
        
        Returns:
            Minimal resource dictionary
        """
        name = name or f"mock-resource-{random.randint(1000, 9999)}"
        location = location or 'eastus'
        resource_id = self._generate_resource_id(resource_type, name)
        
        return {
            'id': resource_id,
            'type': resource_type,
            'name': name,
            'location': location,
            'properties': {},
            'tags': {'generated': 'true', 'source': 'synthesizer'}
        }
    
    def _generate_resource_id(
        self,
        resource_type: str,
        name: str,
        subscription_id: str = 'mock-subscription',
        resource_group: str = 'mock-rg'
    ) -> str:
        """Generate ARM resource ID.
        
        Args:
            resource_type: Resource type
            name: Resource name
            subscription_id: Subscription ID
            resource_group: Resource group name
        
        Returns:
            ARM resource ID string
        """
        provider = resource_type.split('/')[0]
        resource_kind = resource_type.split('/')[1] if '/' in resource_type else 'resources'
        
        return (
            f"/subscriptions/{subscription_id}"
            f"/resourceGroups/{resource_group}"
            f"/providers/{provider}/{resource_kind}/{name}"
        )
    
    def synthesize_batch(
        self,
        resource_type: str,
        count: int,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Generate multiple realistic resources.
        
        Args:
            resource_type: Azure resource type
            count: Number of resources to generate
            **kwargs: Passed to synthesize_resource()
        
        Returns:
            List of resource dictionaries
        """
        resources = []
        for i in range(count):
            # Ensure unique names
            if 'name' not in kwargs:
                kwargs_copy = kwargs.copy()
                kwargs_copy['name'] = None  # Let synthesizer generate unique name
                resource = self.synthesize_resource(resource_type, **kwargs_copy)
            else:
                resource = self.synthesize_resource(resource_type, **kwargs)
            resources.append(resource)
        
        return resources
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns.
        
        Returns:
            Dict with pattern statistics
        """
        all_locations = set()
        for dist in self.location_distribution.values():
            all_locations.update(dist.keys())
        
        return {
            'total_resources': len(self.nodes),
            'resource_types': dict(self.type_counts.most_common()),
            'tag_keys_per_type': {
                rt: list(tags.keys())
                for rt, tags in self.tag_patterns.items()
            },
            'locations': sorted(list(all_locations)),
            'properties_per_type': {
                rt: len(props)
                for rt, props in self.property_patterns.items()
            }
        }
    
    def export_patterns(self, output_path: str):
        """Export learned patterns to JSON file for inspection.
        
        Args:
            output_path: Path to write JSON file
        """
        import json
        from pathlib import Path
        
        patterns = {
            'statistics': self.get_statistics(),
            'location_distribution': {
                rt: dict(dist)
                for rt, dist in self.location_distribution.items()
            },
            'tag_patterns': self.tag_patterns,
            'property_patterns': self.property_patterns
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(patterns, f, indent=2, default=str)
        
        logger.info(f"Exported patterns to {output_path}")


class ResponseSynthesizerFactory:
    """Factory for creating ResponseSynthesizer instances from various sources."""
    
    @staticmethod
    def from_snapshot(snapshot_path: str) -> ResponseSynthesizer:
        """Create synthesizer from snapshot file.
        
        Args:
            snapshot_path: Path to snapshot JSON file
        
        Returns:
            ResponseSynthesizer instance
        """
        from pathlib import Path
        from ..scenarios.snapshot_manager import SnapshotManager
        
        manager = SnapshotManager()
        nodes, _ = manager.load_snapshot(Path(snapshot_path))
        
        return ResponseSynthesizer(nodes)
    
    @staticmethod
    def from_state_manager(state_manager) -> ResponseSynthesizer:
        """Create synthesizer from current state.
        
        Args:
            state_manager: StateManager instance
        
        Returns:
            ResponseSynthesizer instance
        """
        try:
            from ..core.state import GenericResource
            
            # Convert GenericResource objects to node-like objects
            resources = GenericResource.objects.all()
            
            # Create simple node objects
            class SimpleNode:
                def __init__(self, resource):
                    self.type = resource.resource_type
                    self.name = resource.name
                    self.location = resource.location
                    self.properties = resource.properties
                    self.tags = resource.tags
            
            nodes = [SimpleNode(r) for r in resources]
            return ResponseSynthesizer(nodes)
            
        except Exception as e:
            logger.warning(f"Failed to load from state manager: {str(e)}")
            return ResponseSynthesizer([])
