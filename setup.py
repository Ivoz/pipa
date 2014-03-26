import re
import sys

from setuptools import setup

if sys.version_info < (3,):
    sys.exit('pipa can only run on Python 3 or later.')

readme = open('README.rst', encoding='utf-8').read()

init = open('pipa/__init__.py', encoding='utf-8').read()
match = re.search("^__version__ = '(?P<version>[^']*)'$", init, re.M)
version = match.group('version')

requires = ['cherrypy', 'pyOpenSSL', 'Jinja2']


setup(
    name='pipa',
    version=version,
    description='Simple HTTPS PyPI server',
    license='MIT',
    author='Matthew Iversen',
    author_email='matt@notevencode.com',
    url='https://pypi.python.org/pypi/pipa',
    long_description=readme,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Archiving :: Mirroring",
    ],
    install_requires=requires,
    packages=['pipa'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pipa = pipa:main',
        ],
    },
)
