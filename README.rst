Landsat-ESPA-util
=================

*Interface to USGS and ESPA APIs for Landsat surface reflectance data
ordering*


.. image:: https://travis-ci.org/loicdtx/lsru.svg?branch=master
    :target: https://travis-ci.org/loicdtx/lsru

.. image:: https://badge.fury.io/py/lsru.svg
    :target: https://badge.fury.io/py/lsru

.. image:: https://readthedocs.org/projects/lsru/badge/?version=latest
    :target: https://lsru.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


Online doc at `lsru.readthedocs.io <https://lsru.readthedocs.io/en/latest/>`__

Before, downloading Landsat surface reflectance data for a given area
meant:

- Manually querying the sceneIDs on Earth Explorer
- Saving these lists of sceneIDs to text files
- Manually uploading these files to ESPA to place the order
- Downloading the processed data with a download manager

Now, thanks to `USGS
API <https://earthexplorer.usgs.gov/inventory/documentation/json-api>`__,
and `espa API <https://github.com/USGS-EROS/espa-api>`__ it can all be
done programtically.


Example
-------

Send a spatio-temporal query to the Usgs API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used to retrieve a list of available scenes metadata


.. code:: python

    from lsru import Usgs
    import datetime

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

    # Extract Landsat scene ids for each hit from the metadata
    scene_list = [x['displayId'] for x in scene_list]


Place a processing order to Espa
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The scene list can be used to send a processing order to Espa via the Espa API. 
Many options are available (full scene, pixel resizing, reprojection, cropping).


Order full scenes


.. code:: python

    from lsru import Espa
    from pprint import pprint

    # Instantiate Espa class
    espa = Espa()

    # Place order (full scenes, no reprojection, sr and pixel_qa)
    order = espa.order(scene_list=scene_list, products=['sr', 'pixel_qa'])
    print(order.orderid)

    # espa-loic.dutrieux@wur.nl-10212018-102816-245'

Check current orders status

.. code:: python

    for order in espa.orders:
        # Orders have their own class with attributes and methods
        print('%s: %s' % (order.orderid, order.status))

    # espa-loic.dutrieux@wur.nl-10222018-062836-330: ordered
    # espa-loic.dutrieux@wur.nl-10212018-174321-508: complete
    # espa-loic.dutrieux@wur.nl-10212018-174430-792: complete
    # espa-loic.dutrieux@wur.nl-10212018-102816-245: complete
    # espa-loic.dutrieux@wur.nl-10182018-100137-786: complete


Download completed orders. When Espa finishes pre-processing an order, its status 
changes to ``complete``, we can then download the processed scenes.

.. code:: python

    for order in espa.orders:
        if order.is_complete:
            order.download_all_complete('/media/landsat/download/dir')

It is also possible order processing with reprojection, cropping, resizing, etc

.. code:: python

    # Inspect aea projection parameters
    pprint(espa.projections['aea'])
    # Define projection parameters
    proj_params = {'aea': {'central_meridian': 3.8,
                           'datum': 'wgs84',
                           'false_easting': 0,
                           'false_northing': 0,
                           'latitude_of_origin': 43.7,
                           'standard_parallel_1': 43,
                           'standard_parallel_2': 44}}
    # Place order
    order_meta = espa.order(scene_list=scene_list, products=['sr', 'pixel_qa'],
                            note='cropped order with resampling', projection=proj_params,
                            extent=bbox, resolution=60)


Installation
------------


Activate a virtualenv (optional but preferable) and run:

.. code:: sh

    pip install lsru


Setup
-----

The package requires a configuration file in which usgs credentials are written. 
By default the file is called ``~/.lsru`` (this can be modified if you want to join 
this configuration with the configuration of another project) and has the following structure.

::

    [usgs]
    username=your_usgs_username
    password=your_very_secure_password



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


.. figure:: https://i.imgflip.com/1c7eet.jpg
   :alt:
