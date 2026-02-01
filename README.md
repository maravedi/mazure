# Mazure - [Moto](https://github.com/spulec/moto) for Azure

[![Build Status](https://cloud.drone.io/api/badges/tinvaan/mazure/status.svg)](https://cloud.drone.io/tinvaan/mazure)

A library that allows you to mock Azure services.

[![Demo](screenshots/mazure-demo.jpg)](https://www.youtube.com/watch?v=WCLCNlima0M)


## Installation
```bash
$ pip install --editable .
```

## Mazure CLI

Mazure now includes a CLI tool to help you synchronize with Azure REST API specifications, generate new service implementations, and check compatibility.

### Prerequisites

For most CLI operations, you need a local copy of the [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) repository.

```bash
git clone https://github.com/Azure/azure-rest-api-specs.git specs/azure-rest-api-specs --depth=1
```

### Commands

#### Sync
Synchronize with the latest Azure API specifications.

```bash
mazure-cli sync --specs-path specs/azure-rest-api-specs
```

Options:
- `--specs-path`: Path to the `azure-rest-api-specs` repository (default: `specs/azure-rest-api-specs`).
- `--auto-generate`: Automatically generate code for detected changes.

#### Generate
Generate a service implementation from a specification.

```bash
mazure-cli generate Microsoft.Compute virtualMachines 2024-03-01
```

Options:
- `--spec-path`: Specific path to the spec file. If not provided, it searches in the default specs directory.

#### List
List available services, providers, and resources from synced specs to find values for the `generate` command.

```bash
mazure list [SERVICE] [PROVIDER] [RESOURCE]
```

Examples:
- `mazure list` (list all services)
- `mazure list compute` (list providers in compute)
- `mazure list compute Microsoft.Compute` (list resources in provider)
- `mazure list compute Microsoft.Compute virtualMachines` (list versions)

#### Coverage
Show the current API coverage report.

```bash
mazure-cli coverage
```

#### Serve
Start the Mazure mock server to emulate Azure APIs locally.

```bash
mazure serve
```

Options:
- `--port`: Port to run the server on (default: 5050).
- `--host`: Host to run the server on (default: 0.0.0.0).

#### Status
Show currently generated service implementations and their configured routes.

```bash
mazure status
```

#### Compatibility
Check API version compatibility against the local implementations.

```bash
mazure compatibility --specs-path specs/azure-rest-api-specs
```

Options:
- `--specs-path`: Path to the `azure-rest-api-specs` repository.
- `--output`: Output the report to a JSON file.

## Making REST Calls

Once you have started the mock server using `mazure serve`, you can interact with it using any HTTP client (like `curl`, Postman, or various Azure SDKs).

### Base URL
The mock server runs by default on `http://localhost:5050`.

### Example: Listing Virtual Machines
If you have generated the `Microsoft.Compute/virtualMachines` service, you can list VMs using:

```bash
curl -X GET "http://localhost:5050/subscriptions/GUID/resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines?api-version=2024-07-01"
```

### Authentication
The mock server is designed to be a drop-in replacement. It currently accepts any token. You can pass a dummy header if your client requires it:
```bash
curl -H "Authorization: Bearer mock-token" ...
```

### Execution methods

You can execute Mazure using any of the following methods:
- `mazure <command>` (if installed via pip)
- `python -m mazure <command>`
- `mazure-cli <command>`

## Library Usage

`Mazure` provides two modes of operation. It can be used as a <br/>
- Context Manager
- Function Decorator

<br/>

Imagine a test setup as follows. To this
```python
import uuid
import secrets
import unittest

from azure.identity import ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters


class TestStorageAccounts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subscription = str(uuid.uuid4())
        cls.creds = ClientSecretCredential(
            tenant_id=str(uuid.uuid4()),
            client_id=str(uuid.uuid4()),
            client_secret=secrets.token_urlsafe())
        cls.client = StorageManagementClient(cls.creds, cls.subscription)

    def test_create_and_list(self):
        """ TODO
        Creates a storage account & lists all storage accounts in a subscription
        """
```


### Function Decorator
Simply wrap your test function with a `@mazure` decorator.

```python
...
...
from mazure import mazure   # Import the mazure decorator


class TestStorageAccounts(unittest.TestCase):
    ...
    ...

    @mazure
    def test_create_and_list(self):
        accounts = self.client.storage_accounts.list()
        self.assertEqual(len([account for account in accounts]), 0)

        kws = {
            "sku": {"name": "Premium_LRS"},
            "kind": "BlockBlobStorage",
            "location": "eastus",
        }
        self.client.storage_accounts.begin_create(
            'testrg', 'testaccount', StorageAccountCreateParameters(**kws))
        accounts = self.client.storage_accounts.list()
        self.assertGreater(len([account for account in accounts]), 0)
```

### Context Manager
Make use of the `Mazure` class to mock out calls to the Azure API's

```python
...
...

from mazure import Mazure   # Import the Mazure class


class TestStorageAccounts(unittest.TestCase):
    ...
    ...

    def test_create_and_list(self):
        with Mazure():
            accounts = self.client.storage_accounts.list()
            self.assertEqual(len([account for account in accounts]), 0)

            kws = {
                "sku": {"name": "Premium_LRS"},
                "kind": "BlockBlobStorage",
                "location": "eastus",
            }
            self.client.storage_accounts.begin_create(
                'testrg', 'testaccount', StorageAccountCreateParameters(**kws))
            accounts = self.client.storage_accounts.list()
            self.assertGreater(len([account for account in accounts]), 0)
```

## Usage options
With both the decorator and the context manager, Mazure allows you some fine tuning options.

- ### Selective mocking
    You can request only certain services to be mocked in your code. For instance,
    ```python
    @mazure('storage_accounts', 'blob_services')
    def method(self):
        storage = StorageManagementClient(self.creds, self.subscription)
        compute = ComputeManagementClient(self.creds, self.subscription)
        accounts = [acc for acc in storage.storage_accounts.list()]
        machines = [vm for vm in compute.virtual_machines.list_all()]
        return accounts, machines
    ```
    In the above code block, only storage account API calls are mocked out. API calls to any other Azure services will raise an exception.

    When using a context manager, provide a list of services to be mocked
    ```python
    def method(self):
        with Mazure(['storage_accounts', 'blob_services']):
            ...
            ...
    ```
- ### Passthrough option
    To avoid the above scenario, you can use the `allow=True` flag in your decorator, which allows all unmocked API calls to pass through to query the live Azure API's.
    ```python
    @mazure('storage_accounts', 'blob_services', allow=True)
    def method(self):
        ...
        ...
    ```
    When using a context manager, the same functionality is available as follows.
    ```python
    def method(self):
        with Mazure(['storage_accounts', 'blob_services'], allow=True):
            ...
            ...
    ```

## Supported Azure Services

`Mazure` is still very much a work in progress and aims to eventually implement the basic functionality of some of the most commonly used Azure services.

You can use the CLI to see the current coverage:
```bash
mazure-cli coverage
```

At present, `Mazure` implements basic functionality for services including:
- Resource groups
- Storage accounts
- Virtual machines


## Resources
- [Azure REST API sample responses](https://github.com/Azure/azure-rest-api-specs/tree/master/specification)
