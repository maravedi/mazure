import unittest
import json
from mongoengine import connect, disconnect

from .loader import Env
from mazure.services import app
from mazure.services.utils import register, services
from mazure.services.resourcegroups.models import ResourceGroup

class TestSubscriptionsViews(unittest.TestCase):
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

        self.rg = ResourceGroup(
            name='rg1',
            location='eastus',
            subscription=self.env.subscription
        )
        self.rg.save()

    def test_list_subscriptions(self):
        response = self.app.get('/subscriptions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreaterEqual(len(data['value']), 1)

        found = False
        for sub in data['value']:
            if sub['subscriptionId'] == self.env.subscription:
                found = True
                break
        self.assertTrue(found)

    @classmethod
    def tearDownClass(cls):
        disconnect()

if __name__ == '__main__':
    unittest.main()
