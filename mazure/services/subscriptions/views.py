from flask import Blueprint, jsonify
from mazure.services.resourcegroups.models import ResourceGroup
from mazure.services.virtualmachines.models import VirtualMachine
from mazure.services.storageaccounts.models import StorageAccount
from mazure.core.state import GenericResource

subscriptions = Blueprint('subscriptions', __name__)

@subscriptions.route('/', methods=['GET'])
def list_subscriptions():
    sub_ids = set()
    for model in [ResourceGroup, VirtualMachine, StorageAccount]:
        try:
            for item in model.objects.all():
                if hasattr(item, 'subscription'):
                    sub_ids.add(item.subscription)
        except Exception: pass

    try:
        for item in GenericResource.objects.all():
             if hasattr(item, 'subscription_id'):
                 sub_ids.add(item.subscription_id)
    except Exception: pass

    results = []
    for sub_id in sub_ids:
        results.append({
            "id": f"/subscriptions/{sub_id}",
            "subscriptionId": sub_id,
            "tenantId": "00000000-0000-0000-0000-000000000000",
            "displayName": f"Subscription {sub_id}",
            "state": "Enabled",
            "authorizationSource": "RoleBased",
        })

    return jsonify({"value": results})
