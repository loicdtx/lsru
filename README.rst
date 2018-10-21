Landsat-ESPA-util
=================

*Interface to USGS and ESPA APIs for Landsat surface reflectance data
ordering*

Before, downloading Landsat surface reflectance data for a given area
meant: - Manually querying the sceneIDs on Earth Explorer - Saving these
lists of sceneIDs to text files - Manually uploading these files to ESPA
to place the order - Downloading the processed data with a download
manager

Now, thanks to `USGS
API <https://earthexplorer.usgs.gov/inventory/documentation/json-api>`__,
and `espa API <https://github.com/USGS-EROS/espa-api>`__ it can all be
done programtically.

Why can't I just retrieve my Landsat data from Earth Explorer, Amazon or Google cloud?
--------------------------------------------------------------------------------------

You can but it will be top of atmosphere (TOA) radiance, not surface
reflectance. If you aim to have a scientific use of the data, you
probably want to have surface reflectance.

The critical part between TOA radiance and surface reflectance is the
atmospheric correction. That means that surface reflectance data are
corrected for atmospheric effects, therefore providing accurate
measurements of the target's spectral properties.

Today (October 2016), there are a few ways to obtain Landsat surface
reflectance data (All of them have been processed by LEDAPS, the
reference high level Landsat processing tool):

1. By ordering them via the ESPA system

-  this is what this utility helps you to do
-  ESPA does on demand pre-processing of full (reprojected) scenes or
   subsets
-  A cloud mask (fmask) and vegetation indices can also be added to the
   order

1. By ordering them from Google Earth Engine

-  GEE has ingested the entire ESPA surface reflectance collection to
   make it available via its platform

1. By downloading TOA data from any source and processing with a local
   installation of LEDAPS

-  Not necessarily trivial

Usage
-----

.. code:: python


    from lsru import Espa, Usgs
    import datetime
    from pprint import pprint

    # Define query extent
    bbox = (3.5, 43.4, 4, 44)

    # Instantiate Usgs class and login
    usgs = Usgs()
    usgs.login()

    # Query the Usgs api to find scene intersecting with the spatio-temporal window
    scene_list = usgs.search(collection='LANDSAT_8_C1',
                             bbox=bbox,
                             begin=datetime.datetime(2013,1,1),
                             end=datetime.datetime(2016,1,1),
                             max_results=10,
                             max_cloud_cover=40)

    # The espa api require a list of scenes names, which are contained in displayId key of scene metadata
    scene_list = [x['displayId'] for x in scene_list]

    # Instantiate Espa class
    espa = Espa()

    # Place order (full scenes, no reprojection, sr and pixel_qa)
    order_meta = espa.order(scene_list=scene_list, products=['sr', 'pixel_qa'])
    pprint(order_meta)

::

    {'orderid': 'espa-loic.dutrieux@wur.nl-10212018-102816-245',
     'status': 'ordered'}

.. code:: python

    from lsru import Espa, Usgs
    import datetime
    from pprint import pprint

    bbox = (3.5, 43.4, 4, 44)

    usgs = Usgs()
    usgs.login()
    # Query the Usgs api to find scene intersecting with the spatio-temporal window
    scene_list = usgs.search(collection='LANDSAT_8_C1',
                             bbox=bbox,
                             begin=datetime.datetime(2013,1,1),
                             end=datetime.datetime(2016,1,1),
                             max_results=10,
                             max_cloud_cover=40)
    # The espa api require a list of scenes names, which are contained in displayId key of scene metadata
    scene_list = [x['displayId'] for x in scene_list]

    # Instantiate Espa class
    espa = Espa()
    # Inspect aea projection parameters
    pprint(espa.projections['aea'])
    # Define projection parameters
    proj_params = {'aea': {'central_meridian': 3.8,
                           'datum': 'wgs84',
                           'false_easting': 0,
                           'false_northing': 0,
                           'latitude_of_origin': 43.7,
                           'standard_parallel_1': 44,
                           'standard_parallel_2': 43}}
    # Place order
    order_meta = espa.order(scene_list=scene_list, products=['sr', 'pixel_qa'],
                            note='cropped order with resampling', projection=proj_params,
                            extent=bbox, resolution=60)
    pprint(order_meta)


Installing landsat-espa-util
----------------------------

First you must have geos and gdal installed.

.. code:: sh

    sudo apt-get install libgdal-dev # This also installs libgeos-dev

Then, preferably in a virtualenv, run:

.. code:: sh

    pip install git+https://github.com/loicdtx/landsat-espa-util.git

Step by step installation from scratch
--------------------------------------

If you do not have anything setup (virtualenv, gdal, geos, git), follow
the steps below.

.. code:: sh

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

.. figure:: https://i.imgflip.com/1c7eet.jpg
   :alt:
