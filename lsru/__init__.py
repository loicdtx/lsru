import os
import json
import urllib.parse
import datetime
import configparser
import requests

from pprint import pprint

class Usgs(object):
    def __init__(self, version='stable'):
        try:
            config = configparser.ConfigParser()
            config.read(os.path.expanduser('~/.lsru'))
            self.USER = config['usgs']['username']
            self.PASSWORD = config['usgs']['password']
            self.endpoint = '/'.join(['https://earthexplorer.usgs.gov/inventory/json/v',
                                      version])
            self.key = None
            self.key_dt = None
        except Exception as e:
            raise StandardError('There must be a valid configuration file to instantiate this class')


    @property
    def key_age(self):
        if self.key_dt is None:
            raise ValueError('key_age is not defined, you probably need to run login()')
        return datetime.datetime.now() - self.key_dt


    def login(self):
        """Login to the Usgs api
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


    def search(self, collection, bbox, begin=None, end=None, max_cloud_cover=100):
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
                                 'longitude': bbox[2]}}
        if begin is not None:
            params.update(startDate=begin.isoformat())
        if end is not None:
            params.update(endDate=end.isoformat())
        r = requests.post(search_endpoint,
                          data={'jsonRequest': json.dumps(params)})
        return r.json()['data']['results']


