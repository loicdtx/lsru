#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
from setuptools import setup, find_packages
import os

# Parse the version from the main __init__.py
with open('lsru/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


extra_reqs = {'docs': ['sphinx',
                       'sphinx-rtd-theme']}

with codecs.open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(name='lsru',
      version=version,
      description=u"Access the ESPA API for Landsat surface reflectance data ordering and download",
      long_description=readme,
      keywords='landsat, API, espa, usgs',
      author=u"Loic Dutrieux",
      author_email='loic.dutrieux@gmail.com',
      url='https://github.com/loicdtx/landsat-espa-util',
      license='GPLv3',
      classifiers=[
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      packages=find_packages(),
      install_requires=[
          'requests',
      ],
      extras_require=extra_reqs)

