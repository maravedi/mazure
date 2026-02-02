import json
import re
from flask import Blueprint, request, jsonify
from mazure.services.resourcegroups.models import ResourceGroup
from mazure.services.virtualmachines.models import VirtualMachine
from mazure.services.storageaccounts.models import StorageAccount
from mazure.core.state import GenericResource

resourcegraph = Blueprint('resourcegraph', __name__)

@resourcegraph.route('/providers/Microsoft.ResourceGraph/resources', methods=['POST'])
def query_resources():
    try:
        data = request.get_json(force=True)
    except Exception:
        data = {}

    query = data.get('query', '')
    q_lower = query.lower()

    # Handle Subscriptions Query
    if 'resourcecontainers' in q_lower and "type == 'microsoft.resources/subscriptions'" in q_lower:
        subscriptions = set()
        for model in [ResourceGroup, VirtualMachine, StorageAccount]:
            for item in model.objects.all():
                if hasattr(item, 'subscription'):
                    subscriptions.add(item.subscription)
        for item in GenericResource.objects.all():
             if hasattr(item, 'subscription_id'):
                 subscriptions.add(item.subscription_id)

        results = []
        for sub_id in subscriptions:
            results.append({
                "id": f"/subscriptions/{sub_id}",
                "name": sub_id,
                "type": "Microsoft.Resources/subscriptions",
                "subscriptionId": sub_id,
                "tenantId": "00000000-0000-0000-0000-000000000000",
                "properties": {
                    "state": "Enabled",
                    "subscriptionId": sub_id,
                    "tenantId": "00000000-0000-0000-0000-000000000000",
                    "displayName": f"Subscription {sub_id}"
                }
            })

        return jsonify({
            "totalRecords": len(results),
            "count": len(results),
            "data": results,
            "facets": [],
            "resultTruncated": "false"
        })

    # Handle Resources Query
    types = None
    match = re.search(r"type\s+in~\s*\(([^)]+)\)", q_lower)
    if match:
        types_str = match.group(1)
        types = [t.strip().strip("'").strip('"') for t in types_str.split(',')]
    else:
        match = re.search(r"type\s*==\s*['\"]([^'\"]+)['\"]", q_lower)
        if match:
            types = [match.group(1)]

    def to_arg_resource(item, default_type):
        rid = None
        if hasattr(item, 'rid'): rid = item.rid
        elif hasattr(item, 'resource_id'): rid = item.resource_id

        r_type = default_type
        if hasattr(item, 'type'): r_type = item.type
        elif hasattr(item, 'resource_type'): r_type = item.resource_type

        res = {
            "id": rid,
            "name": getattr(item, 'name', 'unknown'),
            "type": r_type,
            "location": getattr(item, 'location', 'unknown'),
            "tags": getattr(item, 'tags', {}),
            "properties": getattr(item, 'properties', {})
        }

        if hasattr(item, 'subscription'): res['subscriptionId'] = item.subscription
        elif hasattr(item, 'subscription_id'): res['subscriptionId'] = item.subscription_id

        if hasattr(item, 'resourceGroup'): res['resourceGroup'] = item.resourceGroup
        elif hasattr(item, 'resource_group'): res['resourceGroup'] = item.resource_group
        elif r_type and r_type.lower() == 'microsoft.resources/resourcegroups':
            res['resourceGroup'] = getattr(item, 'name', None)

        return res

    all_resources = []
    for item in ResourceGroup.objects.all():
        all_resources.append(to_arg_resource(item, 'Microsoft.Resources/resourceGroups'))
    for item in VirtualMachine.objects.all():
        all_resources.append(to_arg_resource(item, 'Microsoft.Compute/virtualMachines'))
    for item in StorageAccount.objects.all():
        all_resources.append(to_arg_resource(item, 'Microsoft.Storage/storageAccounts'))
    for item in GenericResource.objects.all():
        all_resources.append(to_arg_resource(item, getattr(item, 'resource_type', 'unknown')))

    filtered_resources = []
    for r in all_resources:
        if types:
            if r['type'].lower() in types:
                filtered_resources.append(r)
        else:
            filtered_resources.append(r)

    return jsonify({
        "totalRecords": len(filtered_resources),
        "count": len(filtered_resources),
        "data": filtered_resources,
        "facets": [],
        "resultTruncated": "false"
    })
