******************************************
lsru (*Landsat Surface Reflectance Utils*)
******************************************

*Query, order and download Landsat surface reflectance data programmatically*

``lsru`` allows interaction with Usgs and Espa APIs programmatically from python. 
It has 3 main classes:

- ``Usgs`` is the interface to the USGS json API. It is mostly used to query the Landsat catalog for available scenes intersecting with a given spatio-temporal window.
- ``Espa`` is the interface to the ESPA API. Espa is a platform that proposes on demand pre-processing of Landsat data to surface reflectance. Orders can be placed directly from python using that class.
- ``Order`` is the interface to each individual orders placed to the espa platform; it allows retrieving order status and downloading corresponding scenes.


``lsru`` also contains various utilities to smoothen workflows for various use cases of the module.



.. toctree::
   :maxdepth: 1
   :caption: User guide

   user_guide


.. toctree::
   :maxdepth: 1
   :caption: Developer guide

   api


.. toctree::
   :maxdepth: 1
   :caption: Examples

   basic_usage
   example_polygon


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
