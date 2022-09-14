from setuptools import setup

setup(
    name='geovillemsdatabasemodul',
    version='V 19.08.2',
    packages=['test', 'database', 'geoville_ms_database'],
    package_dir={'': 'geoville_ms_database_modul'},
    url='',
    license='GeoVille Software',
    author='Wolfgang Kapferer',
    author_email='kapferer@geoville.com',
    description='GeoVille Microservices Postgres DB Connector',
    install_requires=['psycopg2>=2.8.4']
)
