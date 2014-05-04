from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


# from http://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name='purplex',
      version='0.1',
      description='Pure python lexer implementation.',
      author='Michael Tom-Wing',
      author_email='mtomwing@gmail.com',
      url='https://github.com/mtomwing/purplex',
      packages=['purplex'],
      license='MIT',
      install_requires=['ply==3.4'],
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      zip_safe=False)
