#!/usr/bin/env python3
"""Setup MongoDB indexes for optimal query performance."""

import sys
from mongoengine import connect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_indexes():
    """Create MongoDB indexes for mazure collections."""
    
    try:
        # Connect to MongoDB
        connect('mazure', host='localhost', port=27017)
        logger.info("Connected to MongoDB")
        
        from mazure.core.state import GenericResource
        from mazure.core.relationships import ResourceRelationship
        
        # GenericResource indexes
        logger.info("Creating GenericResource indexes...")
        
        GenericResource.ensure_indexes()
        
        # Additional performance indexes
        collection = GenericResource._get_collection()
        
        # Query by subscription and type (common pattern)
        collection.create_index([
            ('subscription_id', 1),
            ('resource_type', 1)
        ], name='subscription_type_idx')
        
        # Query by location
        collection.create_index([('location', 1)], name='location_idx')
        
        # Query by resource group
        collection.create_index([
            ('subscription_id', 1),
            ('resource_group', 1)
        ], name='subscription_rg_idx')
        
        # Query by tags
        collection.create_index([('tags.environment', 1)], name='tags_environment_idx')
        collection.create_index([('tags.application', 1)], name='tags_application_idx')
        
        # Query by resource_id (for lookups)
        collection.create_index([('resource_id', 1)], name='resource_id_idx', unique=True)
        
        # Full text search on name
        collection.create_index([('name', 'text')], name='name_text_idx')
        
        logger.info("✓ GenericResource indexes created")
        
        # ResourceRelationship indexes
        logger.info("Creating ResourceRelationship indexes...")
        
        ResourceRelationship.ensure_indexes()
        
        rel_collection = ResourceRelationship._get_collection()
        
        # Query relationships by source
        rel_collection.create_index([
            ('source_id', 1),
            ('relation_type', 1)
        ], name='source_relation_idx')
        
        # Query relationships by target
        rel_collection.create_index([
            ('target_id', 1),
            ('relation_type', 1)
        ], name='target_relation_idx')
        
        # Compound index for relationship lookups
        rel_collection.create_index([
            ('source_id', 1),
            ('target_id', 1),
            ('relation_type', 1)
        ], name='relationship_compound_idx', unique=True)
        
        logger.info("✓ ResourceRelationship indexes created")
        
        # Show all indexes
        logger.info("\nAll indexes:")
        for idx in collection.list_indexes():
            logger.info(f"  - {idx['name']}: {idx.get('key', {})}")
        
        logger.info("\n✅ All indexes created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {str(e)}")
        return False


if __name__ == '__main__':
    success = setup_indexes()
    sys.exit(0 if success else 1)
