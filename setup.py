import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from eip712_structs import name, version

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)

setup(
    name=name,
    version=version,
    packages=find_packages(),
    install_requires=requirements,
    cmdclass={"test": PyTest},
)
