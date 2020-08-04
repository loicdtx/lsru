import os
import json
import datetime
from pprint import pprint
from configparser import ConfigParser
import warnings

import requests

from .utils import url_retrieve, url_retrieve_and_unpack

__version__ = "0.6.2"


class Usgs(object):
    """Interface to the Usgs API

    See documentation of the ``search`` method for basic usage

    Args:
        version (str): API version to use, defaults to ``'stable'``
        conf (str): Path of the configuration file containing usgs login
            credentials

    Attributes:
        USER (str): Usgs username
        PASSWORD (str): Usgs password
        endpoint (str): API endpoint
        key (str): API key. Required to perform a search and obtained by
            running the ``login()`` method
        key_dt (datetime.datetime): Time at which the key was generated

    """
    def __init__(self, version='stable', conf=os.path.expanduser('~/.lsru')):
        try:
            config = ConfigParser()
            config.read(conf)
            self.USER = config['usgs']['username']
            self.PASSWORD = config['usgs']['password']
            self.endpoint = '/'.join(['https://earthexplorer.usgs.gov/inventory/json/v',
                                      version])
            self.key = None
            self.key_dt = None
        except Exception as e:
            raise FileNotFoundError('There must be a valid configuration file to instantiate this class')

    @property
    def key_age(self):
        """Determines the age of API key

        Returns:
            datetime.timedelta
        """
        if self.key_dt is None:
            raise ValueError('key_age is not defined, you probably need to run login()')
        return datetime.datetime.now() - self.key_dt

    @staticmethod
    def get_collection_name(num):
        """Get Earth Explorer Landsat collection names

        Args:
            num (int): Landsat spacecraft number (4, 5, 7 or 8)

        Returns:
            str: Earth Explorer collection name formated to i.e. pass to the
                search method
        """
        collections = {4: 'LANDSAT_TM_C1',
                       5: 'LANDSAT_TM_C1',
                       7: 'LANDSAT_ETM_C1',
                       8: 'LANDSAT_8_C1'}
        return collections[num]

    def login(self):
        """Login to the Usgs api

        This method is necessary to obtain an API key (automatically saved in
        the ``key`` attribute), and send other queries to the API

        Return:
            bool: True if query was successful, False otherwise
        """
        login_endpoint = '/'.join([self.endpoint, 'login'])
        r = requests.post(login_endpoint,
                          data={'jsonRequest': json.dumps({'username': self.USER,
                                                           'password': self.PASSWORD})})
        if r.json()['errorCode'] is not None:
            return False
        self.key = r.json()['data']
        self.key_dt = datetime.datetime.now()
        return True

    def search(self, collection, bbox, begin=None, end=None, max_cloud_cover=100,
               months=None, starting_number=1, max_results=50000):
        """Perform a spatio temporal query on Landsat catalog

        Args:
            collection (str): Landsat collection to query.
                Use LANDSAT_8_C1, LANDSAT_ETM_C1 and LANDSAT_TM_C1 for OLI, ETM+,
                and TM respectively
            bbox (tuple): A bounding box in the form of a tuple (left, bottom,
                right, top)
            begin (datetime.datetime): Optional begin date
            end (datetime.datetime): Optional end date
            max_cloud_cover (int): Cloud cover threshold to use for the query
            months (list): List of month indices (1,12) for only limiting the query
                to these months
            max_results (int): Maximum number of scenes to return
            starting_number (int): Used to determine the result number to start
                returning from. Is meant to be used when the total number of hits
                is higher than ``max_results``, to return results in a paginated
                fashion

        Example:
            >>> from lsru import Usgs
            >>> import datetime
            >>> usgs = Usgs()
            >>> usgs.login()
            >>> scene_list = usgs.search(collection='LANDSAT_8_C1',
            >>>                          bbox=(3.5, 43.4, 4, 44),
            >>>                          begin=datetime.datetime(2012,1,1),
            >>>                          end=datetime.datetime(2016,1,1))
            >>> print(scene_list)


        Returns:
            list: List of scenes with complete metadata
        """
        if self.key_age > datetime.timedelta(0, 3600):
            raise ValueError('Api key has probably expired (1 hr), re-run the login method')
        search_endpoint = '/'.join([self.endpoint, 'search'])
        params = {'apiKey': self.key,
                  'node': 'EE',
                  'datasetName': collection,
                  'maxCloudCover': max_cloud_cover,
                  'lowerLeft': {'latitude': bbox[1],
                                'longitude': bbox[0]},
                  'upperRight': {'latitude': bbox[3],
                                 'longitude': bbox[2]},
                  'maxResults': max_results,
                  'startingNumber': starting_number}
        if begin is not None:
            params.update(startDate=begin.isoformat())
        if end is not None:
            params.update(endDate=end.isoformat())
        if months is not None:
            params.update(months=months)
        r = requests.post(search_endpoint,
                          data={'jsonRequest': json.dumps(params)})
        return r.json()['data']['results']


class _EspaBase(object):
    """Interface to the Espa API (metaclass)

    Espa is a platform providing on demand pre-processing of Landsat surface
    data. This class uses the API of the espa platform to query and place orders
    programatically

    Attributes:
        USER (str): Usgs username
        PASSWORD (str): Usgs password
        host (str): API host url

    Args:
        conf (str): Path of the config file containing usgs credentials
    """
    def __init__(self, conf):
        try:
            config = ConfigParser()
            config.read(conf)
            self.USER = config['usgs']['username']
            self.PASSWORD = config['usgs']['password']
            self.host = 'https://espa.cr.usgs.gov/api/v1'
            self.conf = conf
        except Exception as e:
            raise FileNotFoundError('There must be a valid configuration file to instantiate this class')

    def _request(self, endpoint, verb='get', body=None):
        """Generic interface to ESPA api

        Adapted from Jake Brinkmann's example in
        https://github.com/USGS-EROS/espa-api/blob/master/examples/api_demo.ipynb

        Args:
            endpoint (str): Api endpoint to call
            verb (str): Request verb (get, post, put ...)
            body (dict): Data to pass to the request
        """
        auth_tup = (self.USER, self.PASSWORD)
        response = getattr(requests, verb)('/'.join([self.host,  endpoint]),
                                           auth=auth_tup, json=body)
        data = response.json()
        if isinstance(data, dict):
            messages = data.pop("messages", None)
            if messages:
                pprint(messages)
        response.raise_for_status()
        return data


class Espa(_EspaBase):
    """Interface to the Espa API

    Espa is a platform providing on demand pre-processing of Landsat surface
    data. This class uses the API of the espa platform to query and place orders
    programatically

    Attributes:
        USER (str): Usgs username
        PASSWORD (str): Usgs password
        host (str): API host url

    Args:
        conf (str): Path of the config file containing usgs credentials
    """
    def __init__(self, conf=os.path.expanduser('~/.lsru')):
        super(Espa, self).__init__(conf=conf)
        self._projections = None
        self._formats = None
        self._resampling_methods = None
        self._user = None

    def order(self, scene_list, products, format='gtiff', note=None,
              resampling='nn', resolution=None, projection=None,
              extent=None, extent_units='dd', verbose=False):
        """Place a pre-procesing order to espa

        Args:
            scene_list (list): List of Landsat scene ids
            products (list): List of products to order for pre-processing
                See ``Espa.get_available_products()`` to get information on available
                products
            format (str): Pre-processing file format. See Espa.formats for information
                on available formats
            note (str): Optional human readable message to pass to the order
            resampling (str): Resamping method to be used when reprojecting or
                resizing ordered images. See ``Espa.resampling_methods`` for valid
                values.
            resolution (float): Ouput resolution (optional). If specified, the
                pre-processing order will be resized to the specified resolution.
                If set to None (default), no resizing is performed and products
                are processed at their original resolution (usually 30m).
            projection (dict): Optional dictionary with projection name and
                projection parameter values. Ordered products are re-projected
                to the specified projection when set. See ``Espa.projections``
                for list and format of supported projections
            extent (tuple): Bounding box to use to crop the pre-processed products
                bounding box is in the form of a (left, bottom, right, top) tuple.
                This is optional and requires a projection to be set.
            extent_units (str): Units of the provided extent. ``'dd'`` (decimal
                degrees) is the default. If ```meters'`` bounds are specified
                according to the coordinate reference system space.
            verbose (bool): Prints the json body being sent. Useful for debugging
                purposes

        Example:
            >>> from lsru import Espa, Usgs
            >>> import datetime
            >>> espa = Espa()
            >>> usgs = Usgs()
            >>> usgs.login()
            >>> scene_list = usgs.search(collection='LANDSAT_8_C1',
            ...                          bbox=(3.5, 43.4, 4, 44),
            ...                          begin=datetime.datetime(2014,1,1),
            ...                          end=datetime.datetime(2018,1,1))
            >>> scene_list = [x['displayId'] for x in scene_list]
            >>> order = espa.order(scene_list, products=['sr', 'pixel_qa'])


        Return:
            lsru.Order: The method is mostly used for its side effect of placing a
            pre-processing order on the espa platform. It also returns a the
            ``lsru.Order`` instance corresponding to the order
            """
        if note is None:
            note = 'order placed on %s' % datetime.datetime.now().isoformat()
        prods = self.get_available_products(scene_list)
        prods.pop('not_implemented', None)
        # There may be unavailable scenes for ordered products (remove them
        if 'date_restricted' in prods:
            date_restricted = prods.pop('date_restricted')
            for k,v in date_restricted.items():
                if k in products:
                    for scene_id in v:
                        for collection in prods.keys():
                            try:
                                prods[collection]['inputs'].remove(scene_id)
                                warnings.warn('%s removed from order; reason: %s date restriction'
                                              % (scene_id, k))
                            except ValueError:
                                pass
        def prepare_dict(d):
            d['products'] = products
            return d
        params = {k:prepare_dict(v) for k,v in prods.items()}
        params.update(format=format, note=note,
                      resampling_method=resampling)
        if resolution is not None:
            params.update(resize={'pixel_size': resolution,
                                  'pixel_size_units': 'meters'})
        if projection is not None:
            params.update(projection=projection)
            if extent is not None:
                extent_dict = dict(zip(('west', 'south', 'east', 'north'), extent))
                extent_dict.update(units=extent_units)
                params.update(image_extents=extent_dict)
        if verbose:
            pprint(params)
        order_meta = self._request('order', verb='post', body=params)
        return Order(order_meta['orderid'], conf=self.conf)

    @property
    def projections(self):
        """Get a dictionary of projections supported by the platform

        Return:
            dict: Dictionary with key=projections names and values=projection
            attributes
        """
        if self._projections is None:
            self._projections = self._request('projections')
        return self._projections

    def get_available_products(self, scene_list):
        """Get the list of available products for each elements of a list of scene ids

        Args:
            scene_list (list): List of scene ids

        Example:
            >>> from lsru import Espa
            >>> espa = Espa()
            >>> print(espa.get_available_products([
            ...     'LE07_L1TP_029030_20170221_20170319_01_T1'
            ... ]))


        Return:
            dict: Information on products available for each element of the input
                list provided
        """
        return self._request('available-products', body={'inputs': scene_list})

    @property
    def formats(self):
        """Get a list of file formats supported by the platform

        Returns:
            list: List of strings corresponding to the formats names
        """
        if self._formats is None:
            self._formats = self._request('formats')
        return self._formats

    @property
    def resampling_methods(self):
        """Get a list of resamling methods suported by the platform

        Returns:
            list: List of resampling methods
        """
        if self._resampling_methods is None:
            self._resampling_methods = self._request('resampling-methods')
        return self._resampling_methods

    @property
    def user(self):
        """Get Usgs user details

        Returns:
            dict: Usgs user information
        """
        if self._user is None:
            self._user = self._request('user')
        return self._user

    @property
    def orders(self):
        """Get a list of current orders

        Returns:
            list: List of ``lsru.Order``, each one corresponding to an order with
            ordered or complete status (purged orders are not listed)
        """
        order_list = self._request('list-orders',
                                   body={'status': ['complete', 'ordered']})
        return [Order(x, conf=self.conf) for x in order_list]


class Order(_EspaBase):
    """Class to deal with espa orders

    Attributes:
        orderir (str): Espa order ID

    Args:
        orderid (str): Espa order ID
        conf (str): Path to file containing usgs credentials
    """
    def __init__(self, orderid, conf=os.path.expanduser('~/.lsru')):
        super(Order, self).__init__(conf=conf)
        self.orderid = orderid

    @property
    def status(self):
        """Get the current status of the order

        Return:
            str: Order status (e.g. ``ordered``, ``complete``, ``purged``)
        """
        return self._request('order-status/%s' % self.orderid)['status']

    @property
    def is_complete(self):
        """Check if order has status ``complete``

        Return:
            bool
        """
        return True if self.status == 'complete' else False

    @property
    def items_status(self):
        return self._request('item-status/%s' % self.orderid)[self.orderid]

    @property
    def urls_completed(self):
        """Get list of item's url whose status is complete

        Return:
            list: A list of download urls
        """
        item_list = self.items_status
        url_list = [x['product_dload_url'] for x in item_list
                    if x['status'] == 'complete']
        return url_list

    def cancel(self):
        """Cancel the order

        Orders are processed in the order they were placed. Cancelling an order
        may be useful when the order is blocking other orders

        Return:
            dict: The response of the API to the cancellation order
        """
        cancel_request = {"orderid": self.orderid, "status": "cancelled"}
        return self._request('order', verb='put', body=cancel_request)

    def download_all_complete(self, path, unpack=False, overwrite=False,
                              check_complete=True):
        """Download all completed scenes of the order to a folder

        Args:
            path (str): Directory where data are to be downloaded
            unpack (bool): Unpack downloaded archives on the fly
            overwrite (bool): Force overwriting existing files even when they
                already exist? Defaults to False
            check_complete (bool): When local files exist and overwrite is set
                to ``False``, check whether local and remote files sizes match?
                File is re-downloaded when sizes are different. Only makes sense
                if overwrite is set to ``False``. Defaults to ``True``. Also note that
                checking file size takes time (a few millisecons probably), so
                that you'll save time setting this argument to ``False`` in case
                you're sure previous downloads are complete
                Note that this option does not work when ``unpack`` is set to True

        Returns:
            Used for its side effect of batch downloading data, no return
        """
        for url in self.urls_completed:
            filename = url.split('/')[-1]
            try:
                print('Downloading %s' % filename)
                if unpack:
                    url_retrieve_and_unpack(url, path, overwrite=overwrite)
                else:
                    dst = os.path.join(path, filename)
                    url_retrieve(url, dst, overwrite=overwrite,
                                 check_complete=check_complete)
            except Exception as e:
                print('%s skipped. Reason: %s' % (filename, e))


