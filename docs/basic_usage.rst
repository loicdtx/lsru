Basic Usage
===========


This example shows how to query the data from a bounding box, order surface reflectance processing for full scenes without reprojection and download.

Define variables and query available scenes to Usgs
---------------------------------------------------

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
--------------------------------

The scene list can be used to send a processing order to Espa via the Espa API. 

.. code:: python

    from lsru import Espa
    from pprint import print

    # Instantiate Espa class
    espa = Espa()

    # Place order (full scenes, no reprojection, sr and pixel_qa)
    order = espa.order(scene_list=scene_list, products=['sr', 'pixel_qa'])
    print(order.orderid)

    # espa-loic.dutrieux@wur.nl-10212018-102816-245'

Check current orders status
---------------------------

.. code:: python

    for order in espa.orders:
        # Orders have their own class with attributes and methods
        print('%s: %s' % (order.orderid, order.status))

    # espa-loic.dutrieux@wur.nl-10222018-062836-330: ordered
    # espa-loic.dutrieux@wur.nl-10212018-174321-508: complete
    # espa-loic.dutrieux@wur.nl-10212018-174430-792: complete
    # espa-loic.dutrieux@wur.nl-10212018-102816-245: complete
    # espa-loic.dutrieux@wur.nl-10182018-100137-786: complete


Download completed orders
-------------------------

When Espa finishes pre-processing an order, its status 
changes to ``complete``, we can then download the processed scenes.

.. code:: python

    for order in espa.orders:
        if order.is_complete:
            order.download_all_complete('/media/landsat/download/dir')
