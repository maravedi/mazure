import mongoengine as db
from datetime import datetime
from typing import Dict, Any, Optional, List

class GenericResource(db.DynamicDocument):
    resource_id = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    resource_type = db.StringField(required=True)
    subscription_id = db.StringField(required=True)
    resource_group = db.StringField(required=True)
    location = db.StringField(required=True)
    tags = db.DictField()
    properties = db.DictField()
    api_version = db.StringField()
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'resources',
        'indexes': [
            'resource_id',
            ('subscription_id', 'resource_group', 'resource_type'),
            ('subscription_id', 'resource_type')
        ]
    }

    def to_arm_dict(self):
        """Convert to Azure Resource Manager dictionary format"""
        data = {
            'id': self.resource_id,
            'name': self.name,
            'type': self.resource_type,
            'location': self.location,
            'tags': self.tags,
            'properties': self.properties
        }

        # Add dynamic fields
        excluded_fields = {
            'id', 'resource_id', 'name', 'resource_type', 'subscription_id',
            'resource_group', 'location', 'tags', 'properties', 'api_version',
            'created_at', 'updated_at', '_id', '_cls'
        }

        for key in self._data:
            if key not in excluded_fields:
                data[key] = self._data[key]

        return data

class StateManager:
    def __init__(self):
        # Assumes MongoEngine connection is already setup by the app
        pass

    async def create_resource(
        self,
        resource_type: str,
        subscription_id: str,
        resource_group: str,
        name: str,
        properties: Dict[str, Any],
        location: str,
        tags: Optional[Dict[str, str]] = None,
        api_version: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ) -> GenericResource:

        if not resource_id:
            resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{resource_type}/{name}"

        # Check if exists
        existing = GenericResource.objects(resource_id=resource_id).first()
        if existing:
             # If exists, we should probably update it or raise error.
             # For create_resource, let's assume it might overwrite or fail.
             # But the service template checks existence first.
             pass

        resource = GenericResource(
            resource_id=resource_id,
            name=name,
            resource_type=resource_type,
            subscription_id=subscription_id,
            resource_group=resource_group,
            location=location,
            properties=properties,
            tags=tags or {},
            api_version=api_version,
            **kwargs
        )
        resource.save()
        return resource

    async def get_resource(
        self,
        subscription_id: str,
        resource_group: str,
        resource_type: str,
        name: str,
        resource_id: Optional[str] = None
    ) -> Optional[GenericResource]:

        if not resource_id:
            resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{resource_type}/{name}"
        return GenericResource.objects(resource_id=resource_id).first()

    async def update_resource(
        self,
        resource_id: str,
        properties: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> GenericResource:

        resource = GenericResource.objects(resource_id=resource_id).first()
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")

        if properties:
            resource.properties.update(properties)

        if tags is not None:
            resource.tags = tags

        for key, value in kwargs.items():
            setattr(resource, key, value)

        resource.updated_at = datetime.utcnow()
        resource.save()
        return resource

    async def delete_resource(
        self,
        subscription_id: str,
        resource_group: str,
        resource_type: str,
        name: str,
        resource_id: Optional[str] = None
    ) -> bool:

        if not resource_id:
            resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{resource_type}/{name}"
        result = GenericResource.objects(resource_id=resource_id).delete()
        return result > 0

    async def list_resources(
        self,
        subscription_id: str,
        resource_group: Optional[str],
        resource_type: str
    ) -> List[GenericResource]:

        query = {'subscription_id': subscription_id, 'resource_type': resource_type}
        if resource_group:
            query['resource_group'] = resource_group

        return list(GenericResource.objects(**query))
