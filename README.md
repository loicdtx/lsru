# Landsat-ESPA-util
*Interface to USGS and ESPA APIs for Landsat surface reflectance data ordering*

Before, downloading Landsat surface reflectance data for a given area meant:
- Manually querying the sceneIDs on Earth Explorer
- Saving these lists of sceneIDs to text files
- Manually uploading these files to ESPA to place the order
- Downloading the processed data with a download manager

Now, thanks to [USGS API](https://earthexplorer.usgs.gov/inventory/documentation/json-api), and [espa API](https://github.com/USGS-EROS/espa-api) it can all be done programtically.

## Why can't I just retrieve my Landsat data from Earth Explorer, Amazon or Google cloud?

You can but it will be top of atmosphere (TOA) radiance, not surface reflectance. If you aim to have a scientific use of the data, you probably want to have surface reflectance.

The critical part between TOA radiance and surface reflectance is the atmospheric correction. That means that surface reflectance data are corrected for atmospheric effects, therefore providing accurate measurements of the target's spectral properties.

Today (October 2016), there are a few ways to obtain Landsat surface reflectance data (All of them have been processed by LEDAPS, the reference high level Landsat processing tool):

1. By ordering them via the ESPA system
  - this is what this utility helps you to do
  - ESPA does on demand pre-processing of full (reprojected) scenes or subsets
  - A cloud mask (fmask) and vegetation indices can also be added to the order
1. By ordering them from Google Earth Engine
  - GEE has ingested the entire ESPA surface reflectance collection to make it available via its platform 
1. By downloading TOA data from any source and processing with a local installation of LEDAPS
  - Not necessarily trivial


## Usage


## Installing landsat-espa-util

First you must have geos and gdal installed.

```sh
sudo apt-get install libgdal-dev # This also installs libgeos-dev
```

Then, preferably in a virtualenv, run:

```sh
pip install git+https://github.com/loicdtx/landsat-espa-util.git
```

## Step by step installation from scratch

If you do not have anything setup (virtualenv, gdal, geos, git), follow the steps below.

```sh
# Install gdal and geos (geos directly comes as a dependency)
$ sudo apt-get install libgdal-dev

# Install pip (a package manager for python) and git (required to install directly from github)
$ sudo apt-get install python-pip git

# Install virtualenv (virtual environments for python projects)
$ sudo pip install virtualenv

# Install virtualenvwrapper (Makes working with virtualenv easier)
$ sudo pip install virtualenvwrapper

# Finish setting up virtualenvwraper (of course if you use a different shell, export to the right config file)
$ echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
$ source ~/.bashrc

# Create a virtual environement
$ mkvirtualenv landsat_download

# You are now in the virtual environment
# You can exit it by running 'deactivate'
# And get back to it with 'workon landsat_download'

# Install
(landsat_download)$ pip install git+https://github.com/loicdtx/landsat-espa-util.git

# As long as you stay in the virtual environment you can run the lsru commands
(landsat_download)$ lsru --help

# Exist virtualenv
(landsat_download)$ deactivate
$
```

![](https://i.imgflip.com/1c7eet.jpg)


