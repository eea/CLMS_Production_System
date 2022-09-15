import os
from setuptools import setup

setup(
    name='geovillerabbitmqmodul',
    version='V 19.10.1',
    packages=['geoville_ms_receiver',
              'geoville_ms_rabbitmqconfig',
              'geoville_ms_publisher'],
    package_dir={'': 'geoville_ms_rabbitmq_modul'},
    url='',
    license='GeoVille Software',
    author='Samuel Carraro',
    author_email='carraro@geoville.com',
    description='GeoVille Microservices RabbitMQ',
    install_requires=["pika", "cryptography"]
)

os.system("pip3 install --index-url https://clcbb:g8phxTCpTDwsUVAftQTN@gitlab.clcplusbackbone.geoville.com/api/v4/projects/25/packages/pypi/simple geovillemsdatabasemodul")
