from setuptools import setup, find_packages

setup(
    name='geoville-storage-gate',
    version='21.8',
    packages=find_packages(exclude=["tests", "*tests.py"]),
    py_modules=['storage_gate'],
    url='',
    license='GeoVille Software',
    author='Johannes Schmid',
    author_email='schmid@geoville.com',
    description='GeoVille Microservices Storage Gate Module for reading '
                'and writing into NetCDF',
    install_requires=['numpy>=1.18.1', 'pandas>=0.25.3', 'geopandas>=0.6.1',
                      'netCDF4>=1.5.3', 'rasterio>=1.1.3', 'affine>=2.3.0',
                      'rasterstats>=0.14.0', 'Shapely>=1.7.0', 'Rtree>=0.9.3',
                      'pyproj>=2.6.1.post1']
)
