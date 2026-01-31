
from flask import Blueprint
from importlib import import_module
from collections import namedtuple
from pathlib import Path

from .exceptions import NotSupported

service = namedtuple('service', ['prefix', 'property', 'blueprint'])


def discover_generated_services(app, api_dir_name='api'):
    """
    Scans the api directory for generated service blueprints.
    Returns a dictionary of category -> [service]
    """
    current_dir = Path(__file__).resolve().parent
    api_dir = current_dir.parent / api_dir_name

    discovered = {}

    if not api_dir.exists():
        return discovered

    for file_path in api_dir.glob('*.py'):
        if file_path.name == '__init__.py':
            continue

        module_name = file_path.stem

        # Mapping provider to category
        # microsoft_compute_virtualmachines -> compute
        parts = module_name.split('_')
        category = 'unknown'
        if len(parts) >= 2 and parts[0] == 'microsoft':
            category = parts[1]
        elif len(parts) >= 1:
            category = parts[0]

        full_module_name = f"mazure.{api_dir_name}.{module_name}"

        try:
            mod = import_module(full_module_name)
            bp = None
            for name in dir(mod):
                attr = getattr(mod, name)
                if isinstance(attr, Blueprint):
                    bp = attr
                    break

            if bp:
                svc = service(None, category, bp)
                if category not in discovered:
                    discovered[category] = []
                discovered[category].append(svc)
        except ImportError as e:
            # print(f"Failed to import {full_module_name}: {e}")
            pass

    return discovered


def combine(app):
    """
    Returns a combined list of azure component and property strings
    """
    components = list(app.config.get('services').keys())
    properties = list(
        service.property
        for service in sum(app.config.get('services').values(), list())
    )
    return sum([components, properties], list())


def services(app, args):
    """
    Returns all services that need to be registered,
    based on a user's decorator usage.
    """
    names = combine(app)
    result = list(app.config.get('services').get('auth'))
    supported = sum(app.config.get('services').values(), list())

    if len(args) == 0:
        return supported

    if not set(args).issubset(set(names)):
        raise NotSupported(set(args).difference(set(names)))

    for name in args:
        if name not in app.config.get('services').keys():
            for service in supported:
                if service.property == name:
                    result.append(service)
        else:
            result.extend(app.config.get('services').get(name))
    return result


def register(app, services):
    """
    Registers the requested set of services onto the main Flask object
    """
    with app.app_context():
        for service in services:
            if not service.prefix:
                app.register_blueprint(service.blueprint)
            else:
                app.register_blueprint(
                    service.blueprint, url_prefix=service.prefix)


def blueprint(app, modname, anchor=".".join(__name__.split('.')[:-1])):
    """
    Returns the Flask blueprint object for a service
    """
    with app.app_context():
        mod = import_module('.%s.views' % modname, anchor)
        for name in dir(mod):
            attr = getattr(mod, name)
            if isinstance(attr, Blueprint):
                return attr
