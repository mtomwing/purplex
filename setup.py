from setuptools import setup
from setuptools.command.test import test as TestCommand
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


setup(name='purplex',
      version='0.2.4',
      description='Pure Python lexer and parser implementation.',
      author='Michael Tom-Wing',
      author_email='mtomwing@gmail.com',
      url='https://github.com/mtomwing/purplex',
      packages=['purplex'],
      license='MIT',
      cmdclass={'test': PyTest},
      install_requires=['six'],
      zip_safe=False)
