import unittest
from mongoengine import get_db, connect, disconnect

from .loader import Env
from mazure.services import app
from mazure.services.utils import register, services
from mazure.core.state import GenericResource

class TestGenericViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We only register generic service to test it in isolation
        register(app, services(app, ['generic']))
        app.config['TESTING'] = True
        cls.app = app.test_client()
        disconnect()
        connect('mazure', host='mongomock://localhost', alias='default')

    def setUp(self):
        self.env = Env.load()
        self.default_db = get_db('default')
        # URL pattern: /subscriptions/<subId>/resourceGroups/<rgName>/providers/<provider>/<type>/<name>
        # Note: Generic service is mounted at /subscriptions
        # So full URL is /subscriptions/<subId>/resourceGroups/<rgName>/providers/<provider>/<path>
        self.base_url = f"/subscriptions/{self.env.subscription}/resourceGroups/testrg/providers"

    def test_create_get_list_generic_resource(self):
        provider = "Microsoft.Test"
        type_ = "myRes"
        name = "res1"

        # URL for instance: .../providers/Microsoft.Test/myRes/res1
        url = f"{self.base_url}/{provider}/{type_}/{name}"

        payload = {
            "location": "eastus",
            "tags": {"env": "test"},
            "properties": {
                "sku": "basic"
            }
        }

        # 1. Create (PUT)
        r = self.app.put(url, json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['name'], name)
        self.assertEqual(data['type'], f"{provider}/{type_}")

        # Verify DB
        resource = GenericResource.objects(name=name).first()
        self.assertIsNotNone(resource)
        self.assertEqual(resource.resource_type, f"{provider}/{type_}")

        # 2. Get (GET)
        r = self.app.get(url)
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['name'], name)

        # 3. List (GET collection)
        # URL: .../providers/Microsoft.Test/myRes
        collection_url = f"{self.base_url}/{provider}/{type_}"
        r = self.app.get(collection_url)
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn('value', data)
        self.assertEqual(len(data['value']), 1)
        self.assertEqual(data['value'][0]['name'], name)

    def test_nested_resource(self):
        provider = "Microsoft.Test"
        parent_type = "myRes"
        parent_name = "res1"
        child_type = "extensions"
        child_name = "ext1"

        # Full type: Microsoft.Test/myRes/extensions
        # Full name: ext1 (in generic resource)
        # Path: myRes/res1/extensions/ext1

        url = f"{self.base_url}/{provider}/{parent_type}/{parent_name}/{child_type}/{child_name}"

        payload = {"properties": {"key": "val"}}

        # Create
        r = self.app.put(url, json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data['name'], child_name)
        self.assertEqual(data['type'], f"{provider}/{parent_type}/{child_type}")

        # Get Instance
        r = self.app.get(url)
        self.assertEqual(r.status_code, 200)

        # List Children
        # URL: .../myRes/res1/extensions
        collection_url = f"{self.base_url}/{provider}/{parent_type}/{parent_name}/{child_type}"
        r = self.app.get(collection_url)
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(len(data['value']), 1)
        self.assertEqual(data['value'][0]['name'], child_name)

    def test_delete_resource(self):
        url = f"{self.base_url}/Microsoft.Test/delRes/res1"
        self.app.put(url, json={})

        r = self.app.delete(url)
        self.assertEqual(r.status_code, 204)

        r = self.app.get(url)
        self.assertEqual(r.status_code, 404)

    def tearDown(self):
        self.default_db.client.drop_database(self.default_db.name)

    @classmethod
    def tearDownClass(cls):
        disconnect('default')

if __name__ == '__main__':
    unittest.main()
