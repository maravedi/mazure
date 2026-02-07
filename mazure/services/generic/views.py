from flask import Blueprint, request, jsonify, make_response
from mazure.core.state import GenericResource
from datetime import datetime

generic = Blueprint('generic', __name__)

def parse_resource_path(provider_namespace, resource_path):
    segments = resource_path.split('/')

    is_collection = (len(segments) % 2 != 0)

    type_segments = []

    # Identify segments
    for i, seg in enumerate(segments):
        if i % 2 == 0:
            type_segments.append(seg)

    resource_type = f"{provider_namespace}/{'/'.join(type_segments)}"

    if is_collection:
        resource_name = None
    else:
        resource_name = segments[-1]

    return is_collection, resource_type, resource_name

@generic.route('/<subscription_id>/resourceGroups/<resource_group>/providers/<provider_namespace>/<path:resource_path>', methods=['GET', 'PUT', 'DELETE'])
def handle_resource(subscription_id, resource_group, provider_namespace, resource_path):
    is_collection, resource_type, resource_name = parse_resource_path(provider_namespace, resource_path)

    full_resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/{provider_namespace}/{resource_path}"

    if request.method == 'GET':
        if is_collection:
            return list_resources(subscription_id, resource_group, resource_type, full_resource_id)
        else:
            return get_resource(full_resource_id)

    elif request.method == 'PUT':
        if is_collection:
            return make_response("Method Not Allowed", 405)
        return create_or_update(subscription_id, resource_group, resource_type, resource_name, full_resource_id)

    elif request.method == 'DELETE':
        if is_collection:
             return make_response("Method Not Allowed", 405)
        return delete_resource(full_resource_id)

def get_resource(resource_id):
    resource = GenericResource.objects(resource_id=resource_id).first()
    if resource:
        return jsonify(resource.to_arm_dict())
    else:
        return make_response(jsonify({'error': 'Resource not found'}), 404)

def list_resources(subscription_id, resource_group, resource_type, collection_id):
    # collection_id is the path to the collection (e.g. .../virtualMachines)
    # We want resources that are children of this collection.
    # Their IDs will start with collection_id + '/'

    prefix = collection_id + '/'
    resources = GenericResource.objects(
        subscription_id=subscription_id,
        resource_group=resource_group,
        resource_type=resource_type,
        resource_id__startswith=prefix
    )

    return jsonify({'value': [r.to_arm_dict() for r in resources]})

def create_or_update(subscription_id, resource_group, resource_type, resource_name, resource_id):
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        data = {}

    existing = GenericResource.objects(resource_id=resource_id).first()

    properties = data.get('properties', {})
    tags = data.get('tags', {})
    location = data.get('location', 'eastus')

    if existing:
        existing.properties = properties
        existing.tags = tags
        existing.location = location
        existing.updated_at = datetime.utcnow()
        existing.save()
        resource = existing
    else:
        resource = GenericResource(
            resource_id=resource_id,
            name=resource_name,
            resource_type=resource_type,
            subscription_id=subscription_id,
            resource_group=resource_group,
            location=location,
            tags=tags,
            properties=properties
        )
        resource.save()

    return jsonify(resource.to_arm_dict())

def delete_resource(resource_id):
    GenericResource.objects(resource_id=resource_id).delete()
    return '', 204
