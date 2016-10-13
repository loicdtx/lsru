# Spatial
import fiona
import pyproj
from shapely import geometry

# Web
import requests
from usgs import api

# Standard Library
from datetime import datetime
import os

# Self
from .util import parseSceneId, makeEspaFileName, makeEeFileName, getUtmZone, mean, filterListByDate, filterListLT4LO8, isValid
from . import KEY_FILE

#debug
from pprint import pprint


def querySceneLists(collection, ll, ur, start_date, end_date, api_key):
    # TODO: option to order with just a point. Look back at usgs.api.search options
    """ Send a request to earth explorer api

    Args:
        collection (string) one of 'LSR_LANDSAT_ETM_COMBINED', 'LSR_LANDSAT_8', and 'LSR_LANDSAT_TM'
        ll (dict) lowerLeft corner dict with longitude and latitude keys
        ur (dict) upperRight corner dict with longitude and latitude keys
        dates (strings) with '%Y-%m-%d' format
        api_key (string) usgs api key (retrieve it using the 'usgs login' command line)
    """
    scenes = api.search(collection, 'EE',\
        ll=ll,\
        ur=ur,\
        start_date=start_date,\
        end_date=end_date,\
        api_key=api_key)
    scene_list = []
    for scene in scenes:
        scene_list.append(scene['entityId'])
    return scene_list


class extent_geo(object):
    """Extent class in longlat WGS84
    """
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    @classmethod
    def fromFile(cls, filename):
        with fiona.open(filename) as src:
            meta = src.meta
        Multi = geometry.MultiPolygon([geometry.shape(pol['geometry']) for pol in fiona.open(filename)])
        bounds = geometry.shape(Multi).bounds
        # Projection to longlat
        p1 = pyproj.Proj(**meta.get('crs'))
        p2 = pyproj.Proj(init = 'epsg:4326')
        x,y = pyproj.transform(p1, p2, *zip(bounds[0:2], bounds[2:4]))
        extent = cls(min(x), max(x), min(y), max(y))
        return extent
    @classmethod
    def fromCenterAndRadius(cls, lon_0, lat_0, radius):
        prj = pyproj.Proj(proj='aeqd', lat_0=lat_0, lon_0=lon_0)
        box = geometry.box(-radius, -radius, radius, radius)
        # Project back to longlat
        lngs, lats = prj(*box.exterior.xy, inverse=True)
        # Reformat to 2 dictionaries
        xmin = min(*lngs)
        xmax = max(*lngs)
        ymin = min(*lats)
        ymax = max(*lats)
        extent = cls(xmin, xmax, ymin, ymax)
        return extent
    def getCenterCoords(self):
        """Computes Long Lat coordinates of extent centroid
        
        Returns:
            Dictionary: long, lat dictionary
        """
        return {'long': mean([self.xmin, self.xmax]),
                'lat': mean([self.ymin, self.ymax])}
    def getCenterLong(self):
        """Computes Long coordinate of extent centroid
        
        Returns:
            Int: long coordinate of extent centroid
        """
        return mean([self.xmin, self.xmax])
    def getCorners(self):
        """ Returns a tupple of 2 dicts with ll and ur coordinates
        """
        return ({"longitude": self.xmin, "latitude": self.ymin}, {"longitude": self.xmax, "latitude": self.ymax})


class jsonBuilder(object):
    """Class to incrementaly build a dictionary passed as json to the espa order"""
    def __init__(self, sensor, scene_list,\
        products = ["sr", "sr_ndvi", "cloud", "sr_ndmi", "sr_evi", "sr_savi"],\
        note = None):
        """
        Args:
            sensor (string) one of tm4, tm5, etm7, oli8
            scene_list (list) list of sceneIDs
            products (list of strings)
            note (string)
        """
        if note is None:
            note = "%s order passed on %s" % (sensor, datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
        self.process_dict = {
            sensor : {
            "inputs": scene_list, 
            "products": products
        },
            "format": "gtiff",
            "note": note
        }
    def addProjection(self, proj = 'aea', resampling_method = 'bil', center_coords = None):
        """
        Args:
            proj (string)
            resampling_method (string)
            center_coords (dict) Required for proj = 'aea' only. Dict with long and lat keys
        """
        if proj == 'aea':
            if center_coords is None:
                raise ValueError('With aea projection you must supply a dictionary of center coordinates')
            proj_dict = {"projection": {
                            "aea": {
                                "standard_parallel_1": center_coords['lat'] - 5,
                                "standard_parallel_2": center_coords['lat'] + 5,
                                "central_meridian": center_coords['long'],
                                "latitude_of_origin": center_coords['lat'],
                                "false_easting": 0.0,
                                "false_northing": 0.0,
                                "datum": "wgs84"
                            }
                        },
                        "resampling_method": resampling_method}
        elif proj == 'utm':
            if center_coords is None:
                raise ValueError('I need center coordinates to find the UTM zone')
            zone = getUtmZone(center_coords['long'])
            proj_dict = {"projection": {
                            "utm": {
                                "zone": zone,
                                "zone_ns": "north",
                                "datum": "wgs84"
                            }
                        },
                        "resampling_method": resampling_method}
        else:
            raise ValueError('Projection not yet implmented')
        self.process_dict.update(proj_dict)
    def addResizeOption(self, extent):
        """ Add resize parameters to espa order dictionary dictionary
            
        Args:
            extent (dict) object of class extent_geo
        """
        extent_dict = {"image_extents": {
                            "north": extent.ymax,
                            "south": extent.ymin,
                            "east": extent.xmax,
                            "west": extent.xmin,
                            "units": "dd"
                        }}
        self.process_dict.update(extent_dict)
    def getDict(self):
        """ Retrieve dictionary generated
        """
        return self.process_dict



def orderList(username, password, scene_list, proj, resampling_method, resize, xmin = None, xmax = None, ymin = None, ymax = None, long_0=None, lat_0=None, filename=None, radius=None, debug=False):
    # If no scenes returned by Earth explorer, say it and exist
    if len(scene_list) == 0:
        return "Empty scene List"
    # Check for potentially invalid filenames
    scene_list = [x for x in scene_list if isValid(x)]
    # Ensure that all items in the list belong to the same collection
    scene_list = filterListLT4LO8(scene_list)
    collection = parseSceneId(scene_list[0])['sensor']
    if not all(parseSceneId(scene)['sensor'] == collection.upper() for scene in scene_list):
        raise ValueError('Not all elements of scenelist belong to the same collection')
    # Remove data that cannot be processed to SR
    scene_list_clean = filterListByDate(scene_list)
    # convert sensor to espa conventions
    collection = makeEspaFileName(collection)
    # start building json object for request
    json_class = jsonBuilder(collection, scene_list_clean)
    # 
    if proj:
        if long_0 and lat_0:
            center_coords = {'lat': lat_0, 'long': long_0}
        elif xmin and xmax and ymin and ymax:
            center_coords = extent_geo(xmin, xmax, ymin, ymax).getCenterCoords()
        elif filename:
            center_coords = extent_geo.fromFile(filename).getCenterCoords()
        else:
            center_coords = None
        json_class.addProjection(proj = proj, resampling_method = resampling_method, center_coords = center_coords)
        if resize:
            # resizing is optional but requires that the data be reprojected
            if xmin and xmax and ymin and ymax:
                extent = extent_geo(xmin, xmax, ymin, ymax)
            if long_0 and lat_0 and radius:
                extent = extent_geo.fromCenterAndRadius(long_0, lat_0, radius)
            if filename:
                extent = extent_geo.fromFile(filename)
            json_class.addResizeOption(extent)
    # Cary on with the request
    json = json_class.getDict()
    if debug:
        pprint(json)
    r = requests.post("https://espa.cr.usgs.gov/api/v0/order",\
        auth=(username, password), verify=True, json=json)
    if r.status_code != 200:
        # raise ValueError('Something went wrong with the request')
        return "Something went wrong with that request"
    return r


def getSceneList(collection, long_0, lat_0, radius, filename, end_date, start_date, api_key):
    if api_key is None:
        with open(KEY_FILE) as src:
            api_key = src.read()
    collection = makeEeFileName(collection)
    if long_0 and lat_0:
        extent = extent_geo.fromCenterAndRadius(long_0, lat_0, radius)
    if filename:
        extent = extent_geo.fromFile(filename)
    ll, ur = extent.getCorners()
    lst = querySceneLists(collection, ll, ur, start_date, end_date, api_key)
    return lst

