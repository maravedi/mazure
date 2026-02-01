
from flask import Flask

from .utils import blueprint, service, discover_generated_services


app = Flask('mazure', instance_relative_config=True)
app.config.from_object('mazure.config')
app.config.from_pyfile('config.py', silent=True)

app.config['services'] = dict(
    auth=[
        service(
            None,
            'identity',
            blueprint(app, 'identity')
        )
    ],
    compute=[
        service(
            '/subscriptions',
            'virtual_machine',
            blueprint(app, 'virtualmachines')
        )
    ],
    resources=[
        service(
            '/subscriptions',
            'resource_groups',
            blueprint(app, 'resourcegroups')
        )
    ],
    storage=[
        service(
            '/subscriptions',
            'storage_accounts',
            blueprint(app, 'storageaccounts')
        )
    ]
)

# Load generated services
generated_services = discover_generated_services(app)
for category, services in generated_services.items():
    if category in app.config['services']:
        app.config['services'][category].extend(services)
    else:
        app.config['services'][category] = services
