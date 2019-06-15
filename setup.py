import shlex
import sys
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


NAME = 'eip712-structs'
VERSION = '1.1.0'

install_requirements = [
    'eth-utils>=1.4.0',
    'pysha3>=1.0.2',
]

test_requirements = [
    'coveralls==1.8.0',
    'pytest==4.6.2',
    'pytest-cov==2.7.1',
    'web3==4.9.2',
]


def get_file_text(filename):
    file_path = Path(__file__).parent / filename
    if not file_path.exists():
        return ''
    else:
        file_text = file_path.read_text().strip()
        return file_text


long_description = get_file_text('README.md')


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
    name=NAME,
    version=VERSION,
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
