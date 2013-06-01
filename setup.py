from setuptools import setup
import sys

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Development Status :: 4 - Beta
Natural Language :: English
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Operating System :: MacOS :: MacOS X
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
"""

description = 'Auth module for Tornado'

long_description = open("README.rst").read()

major, minor = sys.version_info[:2]

kwargs = {}
if major >= 3:
    kwargs['use_2to3'] = True

packages = ['tauth']
if "nosetests" in sys.argv:
    packages.append('test')

setup(name='tauth',
      version='0.1',
      packages=packages,
      description=description,
      long_description=long_description,
      author='Waldecir Santos',
      author_email='waldecir@gmail.com',
      url='http://github.com/wsantos/tauth/',
      install_requires=['tornado >= 3'],
      license='http://www.apache.org/licenses/LICENSE-2.0',
      classifiers=filter(None, classifiers.split('\n')),
      keywords='tornado coroutine auth module',
      # use python setup.py nosetests to test
      setup_requires=['nose'],
      **kwargs
)
