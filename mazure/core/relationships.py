"""Resource relationship model for dependency tracking."""

import mongoengine as db
from datetime import datetime
from typing import Optional, List, Dict, Any
from mongoengine import Q


class ResourceRelationship(db.Document):
    """MongoDB model for resource relationships.
    
    Stores edges between resources discovered from Azure, enabling:
    - Cascading delete operations
    - Dependency validation
    - Impact analysis
    - Resource group hierarchies
    """
    
    source_id = db.StringField(required=True, help_text="ARM resource ID or Graph URI of source resource")
    target_id = db.StringField(required=True, help_text="ARM resource ID or Graph URI of target resource")
    relation_type = db.StringField(
        required=True,
        help_text="Type of relationship: contains, depends_on, has_member, has_owner, etc."
    )
    weight = db.FloatField(default=1.0, help_text="Relationship weight/importance (0.0-1.0)")
    metadata = db.DictField(help_text="Additional relationship metadata from discovery")
    created_at = db.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'relationships',
        'indexes': [
            ('source_id', 'relation_type'),
            ('target_id', 'relation_type'),
            ('source_id', 'target_id'),
        ]
    }
    
    def __repr__(self):
        return f"<ResourceRelationship {self.source_id} --[{self.relation_type}]--> {self.target_id}>"
    
    @classmethod
    async def create_relationship(
        cls,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ResourceRelationship':
        """Create a new resource relationship.
        
        Args:
            source_id: Source resource ID
            target_id: Target resource ID
            relation_type: Relationship type
            weight: Relationship weight (default 1.0)
            metadata: Optional metadata dict
        
        Returns:
            Created ResourceRelationship instance
        """
        relationship = cls(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            metadata=metadata or {}
        )
        relationship.save()
        return relationship
    
    @classmethod
    def find_outbound(cls, source_id: str, relation_types: Optional[List[str]] = None) -> List['ResourceRelationship']:
        """Find all outbound relationships from a resource.
        
        Args:
            source_id: Source resource ID
            relation_types: Optional list of relation types to filter by
        
        Returns:
            List of ResourceRelationship instances
        """
        query = {'source_id': source_id}
        if relation_types:
            query['relation_type__in'] = relation_types
        return list(cls.objects(**query))
    
    @classmethod
    def find_inbound(cls, target_id: str, relation_types: Optional[List[str]] = None) -> List['ResourceRelationship']:
        """Find all inbound relationships to a resource.
        
        Args:
            target_id: Target resource ID
            relation_types: Optional list of relation types to filter by
        
        Returns:
            List of ResourceRelationship instances
        """
        query = {'target_id': target_id}
        if relation_types:
            query['relation_type__in'] = relation_types
        return list(cls.objects(**query))
    
    @classmethod
    def delete_for_resource(cls, resource_id: str) -> int:
        """Delete all relationships involving a resource.
        
        Args:
            resource_id: Resource ID to delete relationships for
        
        Returns:
            Number of relationships deleted
        """
        return cls.objects(Q(source_id=resource_id) | Q(target_id=resource_id)).delete()
