from setuptools import setup, find_packages


setup(name='landespa',
      version=0.0.1,
      description=u"Access the ESPA API for Landsat surface reflectance data ordering",
      classifiers=[],
      keywords='',
      author=u"Loic Dutrieux",
      author_email='loic.dutrieux@gmail.com',
      url='https://github.com/loicdtx/landsat-espa-util',
      license='GPLv3',
      packages=find_packages(),
      install_requires=[
          'click',
          'shapely',
          'usgs',
          'requests',
          'pyproj'
      ],
      entry_points="""
      [console_scripts]
      landespa=landespa.scripts.cli:landespa
      """
      )