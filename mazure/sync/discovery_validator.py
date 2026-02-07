"""Validation of mock implementations against live Azure."""

import asyncio
from typing import Dict, Any, List, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class DiscoveryBasedValidator:
    """Validate mock service implementations against discovery data.
    
    Compares mazure mock responses with actual Azure discovery data
    to identify gaps and discrepancies.
    """
    
    def __init__(self, discovery_samples: List[Dict[str, Any]]):
        """Initialize with discovery samples.
        
        Args:
            discovery_samples: List of resources from Azure discovery
        """
        self.samples = discovery_samples
        self.validation_results = []
    
    def validate_resource_type(self, resource_type: str, mock_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate mock responses against discovery samples.
        
        Args:
            resource_type: Azure resource type to validate
            mock_responses: List of mock resource responses
        
        Returns:
            Validation report with gaps and discrepancies
        """
        # Get discovery samples for this type
        discovery = [
            s for s in self.samples
            if s.get('type', '').lower() == resource_type.lower()
        ]
        
        if not discovery:
            return {
                'resource_type': resource_type,
                'status': 'no_samples',
                'message': 'No discovery samples available for validation'
            }
        
        if not mock_responses:
            return {
                'resource_type': resource_type,
                'status': 'no_mocks',
                'message': 'No mock responses provided'
            }
        
        # Extract properties from discovery
        discovery_props = self._extract_property_names(discovery)
        mock_props = self._extract_property_names(mock_responses)
        
        # Calculate coverage
        missing_props = discovery_props - mock_props
        extra_props = mock_props - discovery_props
        coverage_pct = (len(mock_props & discovery_props) / len(discovery_props) * 100) if discovery_props else 0
        
        # Validate property types
        type_mismatches = self._compare_property_types(discovery, mock_responses)
        
        result = {
            'resource_type': resource_type,
            'status': 'validated',
            'discovery_sample_count': len(discovery),
            'mock_sample_count': len(mock_responses),
            'coverage': {
                'percentage': round(coverage_pct, 2),
                'total_properties': len(discovery_props),
                'implemented_properties': len(mock_props & discovery_props),
                'missing_properties': sorted(list(missing_props)),
                'extra_properties': sorted(list(extra_props))
            },
            'type_mismatches': type_mismatches,
            'grade': self._calculate_grade(coverage_pct, len(type_mismatches))
        }
        
        self.validation_results.append(result)
        return result
    
    def generate_report(self) -> str:
        """Generate human-readable validation report.
        
        Returns:
            Formatted report string
        """
        if not self.validation_results:
            return "No validation results available."
        
        lines = [
            "=" * 70,
            "Azure Discovery Validation Report",
            "=" * 70,
            ""
        ]
        
        for result in sorted(self.validation_results, key=lambda r: r.get('coverage', {}).get('percentage', 0), reverse=True):
            rt = result['resource_type']
            cov = result.get('coverage', {})
            grade = result.get('grade', 'N/A')
            
            lines.append(f"\nResource Type: {rt}")
            lines.append(f"Grade: {grade}")
            lines.append(f"Coverage: {cov.get('percentage', 0)}%")
            lines.append(f"  Implemented: {cov.get('implemented_properties', 0)}/{cov.get('total_properties', 0)} properties")
            
            if cov.get('missing_properties'):
                lines.append(f"  Missing properties ({len(cov['missing_properties'])}):"
                lines.append("    " + ", ".join(cov['missing_properties'][:10]))
                if len(cov['missing_properties']) > 10:
                    lines.append(f"    ... and {len(cov['missing_properties']) - 10} more")
            
            if result.get('type_mismatches'):
                lines.append(f"  Type mismatches ({len(result['type_mismatches'])})")
                for mismatch in result['type_mismatches'][:3]:
                    lines.append(f"    - {mismatch['property']}: {mismatch['discovery_type']} → {mismatch['mock_type']}")
        
        lines.append("\n" + "=" * 70)
        lines.append("Summary")
        lines.append("=" * 70)
        
        avg_coverage = sum(r.get('coverage', {}).get('percentage', 0) for r in self.validation_results) / len(self.validation_results)
        lines.append(f"Average Coverage: {avg_coverage:.2f}%")
        lines.append(f"Total Resource Types: {len(self.validation_results)}")
        
        grades = [r.get('grade', 'F') for r in self.validation_results]
        a_count = grades.count('A')
        b_count = grades.count('B')
        c_count = grades.count('C')
        lines.append(f"Grades: {a_count} A's, {b_count} B's, {c_count} C's")
        
        return "\n".join(lines)
    
    def _extract_property_names(self, resources: List[Dict[str, Any]]) -> set:
        """Extract all unique property names from resources."""
        props = set()
        for resource in resources:
            if isinstance(resource.get('properties'), dict):
                props.update(resource['properties'].keys())
        return props
    
    def _compare_property_types(self, discovery: List[Dict], mocks: List[Dict]) -> List[Dict[str, str]]:
        """Compare property types between discovery and mocks."""
        mismatches = []
        
        # Get type distributions
        discovery_types = self._get_property_types(discovery)
        mock_types = self._get_property_types(mocks)
        
        # Compare
        for prop_name in discovery_types.keys() & mock_types.keys():
            disc_type = discovery_types[prop_name].most_common(1)[0][0]
            mock_type = mock_types[prop_name].most_common(1)[0][0]
            
            if disc_type != mock_type:
                mismatches.append({
                    'property': prop_name,
                    'discovery_type': disc_type,
                    'mock_type': mock_type
                })
        
        return mismatches
    
    def _get_property_types(self, resources: List[Dict]) -> Dict[str, Any]:
        """Get property type distributions."""
        from collections import Counter
        
        types = defaultdict(Counter)
        for resource in resources:
            props = resource.get('properties', {})
            if isinstance(props, dict):
                for key, value in props.items():
                    types[key][type(value).__name__] += 1
        
        return types
    
    @staticmethod
    def _calculate_grade(coverage_pct: float, mismatch_count: int) -> str:
        """Calculate letter grade based on coverage and mismatches."""
        # Penalize for mismatches
        adjusted_coverage = coverage_pct - (mismatch_count * 2)
        
        if adjusted_coverage >= 90:
            return 'A'
        elif adjusted_coverage >= 80:
            return 'B'
        elif adjusted_coverage >= 70:
            return 'C'
        elif adjusted_coverage >= 60:
            return 'D'
        else:
            return 'F'
