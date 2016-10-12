import re
import math
from datetime import datetime


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
    'LC8': 'LANDSAT_8', # TODO: this is actually incorect but the correct collection name (LSR_LANDSAT_8) does not work.
                        # Scene IDs should be the same though
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



        



        