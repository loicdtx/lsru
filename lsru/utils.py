import re
import os
from io import BytesIO
import tarfile
from contextlib import closing
from datetime import datetime, date

import requests


def bounds(geom):
    """Return a bounding box from a geometry

    Adapted from https://gis.stackexchange.com/a/90554/17409

    Args:
        geom (dict): Geojson like geometry

    Example:
        >>> from lsru.utils import bounds
        >>> geom = {'coordinates': [[[3.34481, 43.96708],
        ...                          [6.17992, 45.23413],
        ...                          [5.55366, 43.56654],
        ...                          [3.34481, 43.96708]]],
        ...         'type': 'Polygon'}
        >>> print(bounds(geom))

    Returns:
        Tuple: Bounding box (left, bottom, right, top)
    """
    def explode(coords):
        for e in coords:
            if isinstance(e, (float, int)):
                yield coords
                break
            else:
                for f in explode(e):
                    yield f
    x, y = zip(*list(explode(geom['coordinates'])))
    return (min(x), min(y), max(x), max(y))


def geom_from_metadata(meta):
    """Return a geometry from a Landsat scene metadata as returned by USGS api

    Args:
        meta (dict): Landsat scene metadata as returned by Usgs Api

    Example:
        >>> from lsru import Usgs
        >>> from lsru.utils import geom_from_metadata
        >>> import datetime
        >>> from shapely.geometry import shape
        >>> from pprint import pprint

        >>> usgs = Usgs()
        >>> usgs.login()
        >>> scene_list = usgs.search(collection='LANDSAT_8_C1',
        ...                          bbox=(3.5, 43.4, 4, 44),
        ...                          begin=datetime.datetime(2012,1,1),
        ...                          end=datetime.datetime(2016,1,1))
        >>> geom = geom_from_metadata(scene_list[0])
        >>> s = shape(geom)
        >>> pprint(geom)
        >>> print(s.is_valid)

    Returns:
        dict: GeoJson like geometry. CRS is always in longlat (EPSG 4326)
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

    Args:
        id (str): Landsat scene id

    Example:
        >>> from lsru import Usgs
        >>> from lsru.utils import is_valid
        >>> import datetime
        >>> import requests
        >>> from pprint import pprint
        >>> usgs = Usgs()
        >>> usgs.login()
        >>> scene_list = usgs.search(collection='LANDSAT_8_C1',
        ...                          bbox=(3.5, 43.4, 4, 44),
        ...                          begin=datetime.datetime(2012,1,1),
        ...                          end=datetime.datetime(2016,1,1))
        >>> pprint(scene_list[2])
        >>> print(is_valid(scene_list[2]['displayId']))

    Returns:
        bool: Whether the provided scene id is valid or not
    """
    pattern = re.compile(r'(LC08|LE07|LT05|LT04)_[0-9A-Z]{4}_\d{6}_\d{8}_\d{8}_\d{2}_(RT|T1|T2)')
    m = pattern.match(id)
    if m is None:
        return False
    else:
        return True


def url_retrieve(url, filename, overwrite=False, check_complete=True):
    """Generic file download function

    Similar to url_retrieve from standard library with additional checks for
    already existing files and incomplete downloads

    Args:
        url (str): Url pointing to file to retrieve
        filename (str): Local file name under which the downloaded content is
            written
        overwrite (bool): Force overwriting local file even when it already exists?
            Defaults to False
        check_complete (bool): When local file exists and overwrite is set to False,
            check whether local and remote file sizes match? File is re-downloaded
            when sizes are different. Only makes sense if overwrite is set to False.
            Defaults to True

    Returns:
        str: The filename
    """
    # Handle special cases (file already exists, no overwrite, check integrity)
    if os.path.isfile(filename) and not overwrite:
        if not check_complete:
            return filename
        r0 = requests.head(url)
        if os.path.getsize(filename) == int(r0.headers['Content-Length']): # file size matches 
            return filename
    # Proceed to download
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return filename


def url_retrieve_and_unpack(url, path, overwrite=False):
    """Generic function to combine download and unpacking of tar archives

    Downloads the tar archive as a memory object and extracts its content to a
    new directory. Directory name is the remote file name with stripped extension

    Args:
        url (str): Url pointing to tar file to retrieve
        path (str): Path to directory under which a new directory containing the
            archive content will be created
        overwrite (bool): Force overwriting local files even when the output
            directory already exist? Defaults to False

    Returns:
        str: The path containing extracted content
    """
    folder = url.split('/')[-1].split('.')[0]
    path = os.path.join(path, folder)
    if os.path.isdir(path) and not overwrite:
        return path
    r = requests.get(url)
    with closing(r), tarfile.open(fileobj=BytesIO(r.content)) as archive:
        archive.extractall(path=path)
    return path
