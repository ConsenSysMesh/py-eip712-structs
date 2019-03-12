from setuptools import setup, find_packages

from eip712_structs import name, version

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(
    name=name,
    version=version,
    packages=find_packages(),
    install_requires=requirements,
)
