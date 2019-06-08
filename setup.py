import shlex
import sys
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


NAME = 'eip712-structs'
VERSION = '1.0.1rc1'


def get_file_lines(filename, split_lines=True):
    filetext = (Path(__file__).parent / filename).read_text().strip()
    if split_lines:
        filetext = filetext.split('\n')
    return filetext


def parse_requirements(filename):
    """Return requirements from requirements file."""
    # Ref: https://stackoverflow.com/a/42033122/
    requirements = get_file_lines(filename)
    requirements = [r.strip() for r in requirements]
    requirements = [r for r in sorted(requirements) if r and not r.startswith('#')]
    return requirements


install_requirements = parse_requirements('requirements.txt')
test_requirements = parse_requirements('test_requirements.txt')
long_description = get_file_lines('README.md', split_lines=False)


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
