import re
import math
from datetime import datetime, date


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


def filterListByDate(scene_list):
    """Remove scenes that cannot be processed to SR
    
    From http://landsat.usgs.gov//CDR_LSR.php
    Due to missing auxiliary input data and/or necessary thermal data, Surface Reflectance processing cannot be applied to data acquired during the dates listed below.

    Landsat 8
    2015:January 30 to February 19 (DOY 30 to 50)Thermal data unavailable*
     March 2 to March 4 (DOY 61 to 63)Thermal data unavailable

    2016:February 19 to February 27 (DOY 50 to 58)Auxiliary data unavailable
     August 8 to August 10 (DOY 221 to 223)Auxiliary data unavailable
    *Thermal data unavailable for select path/rows; see May 8, 2015 calibration notice for details.

    Landsat 7
    2016:May 30 to June 12 (DOY 151 to 164)Auxiliary data unavailable
    """
    # TODO: Find a cleaner way to perform the filtering
    def expression(x):
        exp = not ((parseSceneId(x)['sensor'] == 'LE7' and date(2016, 05, 30) <= parseSceneId(x)['date'] <= date(2016, 06, 12)) or\
             (parseSceneId(x)['sensor'] == 'LC8' and date(2016, 02, 19) <= parseSceneId(x)['date'] <= date(2016, 02, 27)) or\
             (parseSceneId(x)['sensor'] == 'LC8' and date(2016, 8, 8) <= parseSceneId(x)['date'] <= date(2016, 8, 10)) or\
             (parseSceneId(x)['sensor'] == 'LC8' and date(2015, 01, 30) <= parseSceneId(x)['date'] <= date(2015, 02, 19)) or\
             (parseSceneId(x)['sensor'] == 'LC8' and date(2015, 03, 02) <= parseSceneId(x)['date'] <= date(2015, 03, 04)))
        return exp

    scene_list_clean = [x for x in scene_list if expression(x)]
    return scene_list_clean
        
def filterListLT4LO8(scene_list):
    """Remove LT4 and LO8 entries from a list of sceneIDs

    LO8 cannot be brought to SR, while LT4 and LT5 are the same collection in Earth Explorer
    but need to be ordered separately on espa. Which makes it a bit complex to include.
    """
    scene_list_clean = [x for x in scene_list if (parseSceneId(x)['sensor'] != 'LO8') and (parseSceneId(x)['sensor'] != 'LT4')]
    return scene_list_clean

