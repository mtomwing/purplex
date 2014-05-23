from setuptools import setup
from setuptools.command.test import test as TestCommand
import subprocess
import sys


# from http://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--cov=purplex',
            '--pep8',
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


def latest_git_tag():
    raw_version = subprocess.check_output(['git', 'describe', '--tags'])
    return raw_version.rstrip().decode('ascii')


setup(name='purplex',
      version=latest_git_tag(),
      description='Pure Python lexer implementation.',
      author='Michael Tom-Wing',
      author_email='mtomwing@gmail.com',
      url='https://github.com/mtomwing/purplex',
      packages=['purplex'],
      license='MIT',
      install_requires=['ply==3.4'],
      cmdclass={'test': PyTest},
      zip_safe=False)
