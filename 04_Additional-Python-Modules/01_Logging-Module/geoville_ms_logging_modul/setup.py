import os
from setuptools import setup

setup(
    name='geovillemsloggingmodul',
    version='20.7.1',
    packages=['config_file', 'geoville_ms_logging'],
    package_dir={'': 'geoville_ms_logging_modul'},
    url='',
    license='GeoVille Software',
    author='Patrick Wolf',
    author_email='wolf@geoville.com',
    description='GeoVille Microservices Logging Module'
)

os.system("pip3 install --index-url https://clcbb:g8phxTCpTDwsUVAftQTN@gitlab.clcplusbackbone.geoville.com/api/v4/projects/24/packages/pypi/simple geovillerabbitmqmodul")
