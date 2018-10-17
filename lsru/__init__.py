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
        login_endpoint = '/'.join([self.endpoint, 'login'])
        r = requests.post(login_endpoint,
                          data={'jsonRequest': json.dumps({'username': self.USER,
                                                           'password': self.PASSWORD})})
        if r.json()['errorCode'] is not None:
            return False
        self.key = r.json()['data']
        self.key_dt = datetime.datetime.now()
        return True


    def search(self, bbox):
        if self.key_age > datetime.timedelta(0, 3600):
            raise ValueError('Api key has probably expired (1 hr), re-run the login method')
        pass


