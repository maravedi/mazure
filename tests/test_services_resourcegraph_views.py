import unittest
import json
from mongoengine import connect, disconnect

from .loader import Env
from mazure.services import app
from mazure.services.utils import register, services
from mazure.services.resourcegroups.models import ResourceGroup
from mazure.services.virtualmachines.models import VirtualMachine
from mazure.services.storageaccounts.models import StorageAccount
from mazure.core.state import GenericResource

class TestResourceGraphViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register(app, services(app, []))
        app.config['TESTING'] = True
        cls.app = app.test_client()
        disconnect()
        cls.conn = connect('mazure', host='mongomock://localhost')

    def setUp(self):
        self.env = Env.load()
        ResourceGroup.objects.delete()
        VirtualMachine.objects.delete()
        StorageAccount.objects.delete()
        GenericResource.objects.delete()

        # Seed data
        self.rg = ResourceGroup(
            name='rg1',
            location='eastus',
            subscription=self.env.subscription
        )
        self.rg.save()

        self.vm = VirtualMachine(
            name='vm1',
            location='eastus',
            subscription=self.env.subscription,
            resourceGroup='rg1',
            type='Microsoft.Compute/virtualMachines'
        )
        self.vm.save()

        # GenericResource for subscription check
        self.gen_res = GenericResource(
            resource_id=f"/subscriptions/{self.env.subscription}/resourceGroups/rg1/providers/My.Type/res1",
            name='res1',
            resource_type='My.Type',
            subscription_id=self.env.subscription,
            resource_group='rg1',
            location='eastus',
            properties={}
        )
        self.gen_res.save()

    def test_query_resources_by_type(self):
        query = "where type in~ ('Microsoft.Compute/virtualMachines')"

        response = self.app.post(
            '/providers/Microsoft.ResourceGraph/resources',
            data=json.dumps({'query': query}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['totalRecords'], 1)
        self.assertEqual(data['data'][0]['name'], 'vm1')
        self.assertEqual(data['data'][0]['type'], 'Microsoft.Compute/virtualMachines')

    def test_query_subscriptions(self):
        query = "resourcecontainers | where type == 'microsoft.resources/subscriptions'"

        response = self.app.post(
            '/providers/Microsoft.ResourceGraph/resources',
            data=json.dumps({'query': query}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(data['totalRecords'], 1)
        # check if our subscription is there
        found = False
        for item in data['data']:
            if item['subscriptionId'] == self.env.subscription:
                found = True
                break
        self.assertTrue(found)

    def test_rg_has_resource_group_field(self):
        query = "Resources | where type == 'microsoft.resources/resourcegroups'"

        response = self.app.post(
            '/providers/Microsoft.ResourceGraph/resources',
            data=json.dumps({'query': query}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(data['totalRecords'], 1)

        # Check if the RG we seeded exists and has resourceGroup field
        found = False
        for item in data['data']:
            # Ensure we only got what we asked for
            self.assertEqual(item['type'].lower(), 'microsoft.resources/resourcegroups')

            if item['name'] == 'rg1':
                found = True
                self.assertIn('resourceGroup', item)
                self.assertEqual(item['resourceGroup'], 'rg1')
        self.assertTrue(found)

    @classmethod
    def tearDownClass(cls):
        disconnect()

if __name__ == '__main__':
    unittest.main()
