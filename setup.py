import shlex
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

from eip712_structs import name, version


def filter_empties(l):
    return [i for i in l if i]


with open('requirements.txt', 'r') as f:
    install_requirements = filter_empties(f.readlines())

with open('test_requirements.txt', 'r') as f:
    test_requirements = filter_empties(f.readlines())

with open('README.md', 'r') as f:
    long_description = f.read()


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


class CoverallsCommand(TestCommand):
    description = 'Run the coveralls command'
    user_options = [("coveralls-args=", "a", "Arguments to pass to coveralls")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.coveralls_args = ""

    def run_tests(self):
        import coveralls.cli
        errno = coveralls.cli.main(shlex.split(self.coveralls_args))
        sys.exit(errno)


setup(
    name=name,
    version=version,
    author='AJ Grubbs',
    packages=find_packages(),
    install_requires=install_requirements,
    tests_require=test_requirements,
    cmdclass={
        "test": PyTest,
        "coveralls": CoverallsCommand,
    },
    description='A python library for EIP712 objects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='ethereum eip712 solidity',
    url='https://github.com/ajrgrubbs/py-eip712-structs',
)
