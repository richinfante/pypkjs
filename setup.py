__author__ = 'katharine'

from setuptools import setup, find_packages
from pkg_resources import resource_string

# requirements_str = resource_string(__name__, 'requirements.txt').decode()
# requirements = [line.strip() for line in requirements_str.splitlines()]
# print(requirements)
__version__= None  # Overwritten by executing version.py.
with open('pypkjs/version.py') as f:
    exec(f.read())

setup(name='pypkjs',
      version=__version__,
      description='A Pebble phone app simulator written in Python',
      url='https://github.com/pebble/pypkjs',
      author='Pebble Technology Corporation',
      author_email='katharine@pebble.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
            "backports.ssl-match-hostname==3.4.0.2",
            "gevent==24.11.1",
            "gevent-websocket==0.10.1",
            "greenlet>=0.4.7",
            "peewee==3.17.9",
            "pygeoip==0.3.2",
            "pypng==0.20220715.0",
            "python-dateutil==2.4.1",
            "requests==2.7.0",
            "sh==1.09",
            "six==1.9.0",
            "websocket-client==0.32.0",
            "libpebble2>=0.0.20",
            "netaddr==0.7.18",
            "stpyv8==13.1.201.22",
      ],
      package_data={
          'pypkjs.javascript.navigator': ['GeoLiteCity.dat'],
          'pypkjs.timeline': ['layouts.json'],
      },
      entry_points={
          'console_scripts': [
            'pypkjs=pypkjs.runner.websocket:run_tool'
          ],
      },
      zip_safe=False)
