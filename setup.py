from setuptools import setup

setup(name='purplex',
      version='0.1',
      description='Pure python lexer implementation.',
      author='Michael Tom-Wing',
      author_email='mtomwing@gmail.com',
      url='https://github.com/mtomwing/purplex',
      packages=['purplex'],
      license='MIT',
      install_requires=['ply==3.4'],
      zip_safe=False)
