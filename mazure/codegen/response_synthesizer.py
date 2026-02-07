"""Response synthesis from discovery patterns.

Generates realistic mock resources based on statistical analysis
of historical discovery data.
"""

from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional, Set
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
        else:
            logger.warning("No historical data provided for synthesis")
    
    def _analyze_patterns(self):
        """Analyze patterns in discovered resources."""
        logger.info(f"Analyzing patterns from {len(self.nodes)} resources")
        
        # Resource type frequency
        self.type_counts = Counter(getattr(n, 'type', None) for n in self.nodes)
        
        # Location distribution per type
        self.location_distribution = {}
        for node in self.nodes:
            node_type = getattr(node, 'type', None)
            node_location = getattr(node, 'location', None)
            
            if node_type and node_location:
                if node_type not in self.location_distribution:
                    self.location_distribution[node_type] = Counter()
                self.location_distribution[node_type][node_location] += 1
        
        # Tag patterns
        self.tag_patterns = self._extract_tag_patterns()
        
        # Property patterns per type
        self.property_patterns = self._extract_property_patterns()
        
        logger.info(
            f"Analyzed {len(self.nodes)} resources across "
            f"{len(self.type_counts)} types"
        )
    
    def _extract_tag_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Extract common tag keys and value patterns per resource type.
        
        Returns:
            Dict mapping resource_type -> tag_key -> list of observed values
        """
        patterns = {}
        
        for node in self.nodes:
            node_type = getattr(node, 'type', None)
            node_tags = getattr(node, 'tags', None)
            
            if not node_type or not node_tags:
                continue
            
            if node_type not in patterns:
                patterns[node_type] = {}
            
            for key, value in node_tags.items():
                if key.startswith('_'):  # Skip internal tags
                    continue
                if key not in patterns[node_type]:
                    patterns[node_type][key] = []
                if value and value not in patterns[node_type][key]:
                    patterns[node_type][key].append(value)
        
        return patterns
    
    def _extract_property_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Extract property patterns per resource type.
        
        Returns:
            Dict mapping resource_type -> property_key -> pattern info
        """
        patterns = {}
        
        for node in self.nodes:
            node_type = getattr(node, 'type', None)
            node_props = getattr(node, 'properties', None)
            
            if not node_type or not node_props:
                continue
            
            if node_type not in patterns:
                patterns[node_type] = {}
            
            for key, value in node_props.items():
                if key not in patterns[node_type]:
                    patterns[node_type][key] = {
                        'type': type(value).__name__,
                        'values': [],
                        'null_count': 0
                    }
                
                if value is None:
                    patterns[node_type][key]['null_count'] += 1
                else:
                    # Store sample values (up to 10 unique)
                    if len(patterns[node_type][key]['values']) < 10:
                        if value not in patterns[node_type][key]['values']:
                            patterns[node_type][key]['values'].append(value)
        
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
        similar = [
            n for n in self.nodes 
            if getattr(n, 'type', None) == resource_type
        ]
        
        if not similar:
            logger.warning(
                f"No examples found for {resource_type}. "
                f"Generating minimal resource."
            )
            return self._generate_minimal_resource(
                resource_type, name, location,
                override_properties, override_tags
            )
        
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
                    properties[prop_key] = f"mock-{prop_key}"
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
            if (resource_type in self.location_distribution and 
                self.location_distribution[resource_type]):
                location = random.choices(
                    list(self.location_distribution[resource_type].keys()),
                    weights=list(self.location_distribution[resource_type].values()),
                    k=1
                )[0]
            else:
                location = 'eastus'  # Default fallback
        
        # Generate realistic tags
        tags = {}
        if resource_type in self.tag_patterns:
            for tag_key, values in self.tag_patterns[resource_type].items():
                if random.random() < 0.7:  # 70% chance to include each tag
                    tags[tag_key] = random.choice(values)
        
        # Apply tag overrides
        if override_tags:
            tags.update(override_tags)
        
        # Generate name if not provided
        if not name:
            template_name = getattr(template, 'name', 'resource')
            prefix = template_name.split('-')[0] if '-' in template_name else template_name
            name = f"{prefix}-{random.randint(1000, 9999)}"
        
        return {
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
        location: Optional[str],
        override_properties: Optional[Dict[str, Any]],
        override_tags: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Generate minimal resource when no examples available."""
        return {
            'type': resource_type,
            'name': name or f"mock-{resource_type.split('/')[-1].lower()}-{random.randint(1000, 9999)}",
            'location': location or 'eastus',
            'properties': override_properties or {},
            'tags': override_tags or {}
        }
    
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
        return [
            self.synthesize_resource(resource_type, **kwargs)
            for _ in range(count)
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about learned patterns.
        
        Returns:
            Dict with pattern statistics
        """
        return {
            'total_resources': len(self.nodes),
            'resource_types': dict(self.type_counts.most_common()),
            'tag_keys_per_type': {
                rt: list(tags.keys())
                for rt, tags in self.tag_patterns.items()
            },
            'locations': sorted(set(
                loc
                for dist in self.location_distribution.values()
                for loc in dist.keys()
            )),
            'types_with_patterns': len(self.property_patterns)
        }
    
    def get_common_locations_for_type(self, resource_type: str) -> List[str]:
        """Get most common locations for a resource type.
        
        Args:
            resource_type: Azure resource type
        
        Returns:
            List of locations ordered by frequency
        """
        if resource_type not in self.location_distribution:
            return ['eastus', 'westus2', 'centralus']  # Defaults
        
        return [
            loc for loc, _ in 
            self.location_distribution[resource_type].most_common()
        ]
    
    def get_common_tags_for_type(self, resource_type: str) -> Dict[str, List[str]]:
        """Get common tags for a resource type.
        
        Args:
            resource_type: Azure resource type
        
        Returns:
            Dict mapping tag keys to possible values
        """
        return self.tag_patterns.get(resource_type, {})
