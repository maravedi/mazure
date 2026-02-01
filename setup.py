from setuptools import setup, find_packages
from os.path import join, dirname, abspath


def requirements():
    basedir = abspath(dirname(__file__))
    with open(join(basedir, 'requirements.txt')) as f:
        return f.read().splitlines()


setup(
    name='mazure',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements(),
    entry_points={
        'console_scripts': [
            'mazure=mazure.cli.sync:app',
            'mazure-cli=mazure.cli.sync:app',
        ],
    },
)
