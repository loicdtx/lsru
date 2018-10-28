User Guide
==========

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

