from setuptools import setup, find_packages
import os

# Create directory to store download logs
# if not os.path.exists(os.path.expanduser('~/.landespa')):
#     os.makedirs(os.path.expanduser('~/.landespa'))


setup(name='lsru',
      version='0.2.2',
      description=u"Access the ESPA API for Landsat surface reflectance data ordering and download",
      classifiers=[],
      keywords='landsat, API, espa, usgs',
      author=u"Loic Dutrieux",
      author_email='loic.dutrieux@gmail.com',
      url='https://github.com/loicdtx/landsat-espa-util',
      license='GPLv3',
      packages=find_packages(),
      install_requires=[
          'shapely',
          'fiona',
          'pyproj',
          'usgs',
          'requests',
          'Click',
      ],
      entry_points="""
      [console_scripts]
      lsru=lsru.scripts.cli:lsru
      """
      )
