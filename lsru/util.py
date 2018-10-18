import re
import math
from datetime import datetime, date


def bounds(geom):
    """Return a bounding box from a geometry

    Args:
        geom (dict): Geojson like geometry

    Returns:
        Tuple: Bounding box (left, bottom, right, top)
    """
    pass


def geom_from_metadata(meta):
    """Return a geometry from a Landsat scene metadata as returned by USGS api

    Args:
        meta (dict): Landsat scene metadata as returned by Usgs Api

    Returns:
        dict: GeoJson like geometry. CRS is always in longlat (EPSG:4326)
    """
    geom = {'type': 'Polygon',
            'coordinates': [[
                [meta['lowerLeftCoordinate']['longitude'],
                 meta['lowerLeftCoordinate']['latitude']],
                [meta['upperLeftCoordinate']['longitude'],
                 meta['upperLeftCoordinate']['latitude']],
                [meta['upperRightCoordinate']['longitude'],
                 meta['upperRightCoordinate']['latitude']],
                [meta['lowerRightCoordinate']['longitude'],
                 meta['lowerRightCoordinate']['latitude']],
                [meta['lowerLeftCoordinate']['longitude'],
                 meta['lowerLeftCoordinate']['latitude']]
            ]]}
    return geom


def is_valid(id):
    """Landsat scene id validity checker
    """
    pass


def url_retrieve(url, write_dir):
    """Pretty much a generic file download function
    """
    if url is None:
        return "Missing scene"
    directory = os.path.join(write_dir, url.split('/')[-2])
    if not os.path.exists(directory):
        os.makedirs(directory)
    local_filename = os.path.join(directory, url.split('/')[-1])
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


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
    id_grep = re.compile(".*(LT4|LT5|LE7|LC8|LO8)(\d{3})(\d{3})(\d{7}).*", re.IGNORECASE)
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
    'LC8': 'LANDSAT_8', # TODO: this is actually incorect but the correct collection name (LSR_LANDSAT_8) does not work.
                        # Scene IDs should be the same though
    'LT5': 'LSR_LANDSAT_TM'}
    return collection_name.get(name)

def makeEspaFileName(name):
    name = name.upper()
    collection_name = {
    'LE7': 'etm7',
    'LC8': 'olitirs8',
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



def isValid(id):
    """Check if a sceneID is valid

    We've seen e.g. LT8 in the scene list returned by Earth Explorer API
    That can't pass the checks 

    Args:
        id (string) string containing a Landsat scene ID

    Returns:
        Boolean
    """
    id_grep = re.compile("(LT4|LT5|LE7|LC8|LO8)\d{13}", re.IGNORECASE)
    m = id_grep.match(id)
    if m is None:
        return False
    else:
        return True
