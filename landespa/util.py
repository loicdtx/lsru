import pyproj
from shapely import geometry
from usgs import soap, api
import requests
import re
import math
from datetime import datetime
from pprint import pprint

def xyToBox(center_coords, radius):
    # TODO: add function to generate same outputs from a spatial object read with fiona
    """ Make extent/boundingBox from coordinates and radius

    Define an extent around the point (requires projecting back and forth to a equidistant local projection
    
    Args:
        center_coords (dict) with long and lat keys
        radius (int) square buffer radius in meters

    Returns:
        Tupple of four (lowerLeft dict, upperRight dicts, long coordinates tupple, lat coordinates tupple)
    """
    prj = pyproj.Proj(proj='aeqd', lat_0=center_coords['lat'], lon_0=center_coords['long'])
    box = geometry.box(-radius, -radius, radius, radius)
    # Project back to longlat
    lngs, lats = prj(*box.exterior.xy, inverse=True)
    # Reformat to 2 dictionaries
    ll = {"longitude": min(*lngs), "latitude": min(*lats)}
    ur = {"longitude": max(*lngs), "latitude": max(*lats)}
    return (ll, ur, lngs, lats)

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



def parseSceneId(id):
    """Landsat sceneID parser

    Identifies a typical LandsatID sequence in a string and returns a
    dictionary with information on sensor, date, path and row. The function
    raises an error in case no Landsat scene ID pattern can be found

    Args:
        id (string) string containing a Landsat scene ID

    Returns:
        dictionary: Dictionary containing information on sensor, date, path and row
    """
    id_grep = re.compile(".*(LT4|LT5|LE7|LC8)(\d{3})(\d{3})(\d{7}).*", re.IGNORECASE)
    m = id_grep.search(id)
    if m is None:
        raise ValueError('Landsat ID pattern not found for %s' % id)
    id_meta = {'sensor': m.group(1).upper(),
               'date': datetime.strptime(m.group(4), "%Y%j").date(),
               'path': int(m.group(2)),
               'row': int(m.group(3))}
    return id_meta


def makeEeFileName(name):
    name = name.upper()
    collection_name = {
    'LE7': 'LSR_LANDSAT_ETM_COMBINED',
    'LC8': 'LSR_LANDSAT_8',
    'LT5': 'LSR_LANDSAT_TM'}
    return collection_name.get(name)

def makeEspaFileName(name):
    name = name.upper()
    collection_name = {
    'LE7': 'etm7',
    'LC8': 'oli8',
    'LT5': 'tm5',
    'LT4': 'tm4'}
    return collection_name.get(name)


def getUtmZone(long):
    """Find in which UTM zone is a given location (longitude only)
    """
    zone = math.floor((long + 180)/6) % 60 + 1
    return int(zone)


def mean(numbers):
    return float(sum(numbers)) / len(numbers)


class extent_geo(object):
    """Extent class in longlat WGS84
    """
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
    @classmethod
    def fromFile(cls, file):
        with fiona.open(file) as src:
            meta = src.meta
        Multi = geometry.MultiPolygon([geometry.shape(pol['geometry']) for pol in fiona.open(file)])
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
        if proj is 'aea':
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
        elif proj is 'utm':
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
            extent (dict) dict with keys xmin, xmax, ymin, ymax
        """
        extent_dict = {"image_extents": {
                            "north": extent['ymax'],
                            "south": extent['ymin'],
                            "east": extent['xmax'],
                            "west": extent['xmin'],
                            "units": "dd"
                        }}
        self.process_dict.update(extent_dict)
    def getDict(self):
        """ Retrieve dictionary generated
        """
        return self.process_dict
        