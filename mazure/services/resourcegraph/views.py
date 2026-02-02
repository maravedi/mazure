import json
import re
from flask import Blueprint, request, jsonify
from mazure.services.resourcegroups.models import ResourceGroup
from mazure.services.virtualmachines.models import VirtualMachine
from mazure.services.storageaccounts.models import StorageAccount
from mazure.core.state import GenericResource

resourcegraph = Blueprint('resourcegraph', __name__)

def parse_query(query_str):
    """
    Parses a KQL query string to extract filters.
    Returns a dictionary of filters.
    """
    q_lower = query_str.lower()
    filters = {
        'include_types': [],
        'exclude_types': [],
        'resource_groups': [],
        'tags': {}
    }

    # 1. Handle "tolower(type) == '...'" (Include)
    # Regex looks for: tolower(type) == 'value'
    include_matches = re.findall(r"tolower\(type\)\s*==\s*['\"]([^'\"]+)['\"]", q_lower)
    if include_matches:
        filters['include_types'].extend(include_matches)

    # 2. Handle "tolower(type) != '...'" (Exclude)
    exclude_matches = re.findall(r"tolower\(type\)\s*!=\s*['\"]([^'\"]+)['\"]", q_lower)
    if exclude_matches:
        filters['exclude_types'].extend(exclude_matches)

    # 3. Handle "tolower(resourceGroup) == '...'"
    rg_matches = re.findall(r"tolower\(resourcegroup\)\s*==\s*['\"]([^'\"]+)['\"]", q_lower)
    if rg_matches:
        filters['resource_groups'].extend(rg_matches)

    # 4. Handle "tags['key'] =~ 'value'"
    # Regex looks for: tags['key'] =~ 'value'
    tag_matches = re.findall(r"tags\['([^']+)'\]\s*=~\s*['\"]([^'\"]+)['\"]", q_lower)
    for key, value in tag_matches:
        filters['tags'][key] = value

    # Fallback for legacy queries: "type in~ (...)" or "type == ..."
    if not filters['include_types']:
        match_in = re.search(r"type\s+in~\s*\(([^)]+)\)", q_lower)
        if match_in:
            types_str = match_in.group(1)
            filters['include_types'] = [t.strip().strip("'").strip('"') for t in types_str.split(',')]
        else:
            match_eq = re.search(r"type\s*==\s*['\"]([^'\"]+)['\"]", q_lower)
            if match_eq:
                filters['include_types'] = [match_eq.group(1)]

    return filters

@resourcegraph.route('/providers/Microsoft.ResourceGraph/resources', methods=['POST'])
def query_resources():
    try:
        data = request.get_json(force=True)
    except Exception:
        data = {}

    query = data.get('query', '')
    q_lower = query.lower()

    # Handle Subscriptions Query (Legacy special case)
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

    # Parse Filters
    filters = parse_query(query)

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

    # Gather All Resources
    all_resources = []
    for item in ResourceGroup.objects.all():
        all_resources.append(to_arg_resource(item, 'Microsoft.Resources/resourceGroups'))
    for item in VirtualMachine.objects.all():
        all_resources.append(to_arg_resource(item, 'Microsoft.Compute/virtualMachines'))
    for item in StorageAccount.objects.all():
        all_resources.append(to_arg_resource(item, 'Microsoft.Storage/storageAccounts'))
    for item in GenericResource.objects.all():
        all_resources.append(to_arg_resource(item, getattr(item, 'resource_type', 'unknown')))

    # Apply Filters
    filtered_resources = []
    for r in all_resources:
        keep = True
        r_type_lower = r['type'].lower()
        r_rg_lower = (r.get('resourceGroup') or '').lower()
        r_tags = r.get('tags') or {}

        # 1. Include Types (OR logic)
        if filters['include_types']:
            if r_type_lower not in filters['include_types']:
                keep = False

        # 2. Exclude Types (AND logic)
        if keep and filters['exclude_types']:
            if r_type_lower in filters['exclude_types']:
                keep = False

        # 3. Resource Groups (OR logic)
        if keep and filters['resource_groups']:
            if r_rg_lower not in filters['resource_groups']:
                keep = False

        # 4. Tags (AND logic)
        if keep and filters['tags']:
            for t_key, t_val in filters['tags'].items():
                # t_key is lowercased from query parsing

                # Check if tag exists case-insensitively in r_tags
                # r_tags keys can be anything

                found_val = None
                for r_key, r_val in r_tags.items():
                    if r_key.lower() == t_key:
                        found_val = r_val
                        break

                if found_val is None:
                    keep = False
                    break

                if found_val.lower() != t_val.lower():
                    keep = False
                    break

        if keep:
            filtered_resources.append(r)

    return jsonify({
        "totalRecords": len(filtered_resources),
        "count": len(filtered_resources),
        "data": filtered_resources,
        "facets": [],
        "resultTruncated": "false"
    })
