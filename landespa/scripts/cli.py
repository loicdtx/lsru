import requests
import os
from usgs import api
from datetime import datetime
from landespa.util import xyToBox, querySceneLists, parseSceneId, jsonBuilder, makeEeFileName, makeEspaFileName
import click


today = str(datetime.today().date())
KEY_FILE = os.path.expanduser('~/.usgs')


@click.group()
def landespa():
    pass

@click.command()
@click.option('--username', prompt='USGS username')
@click.option('--password', prompt='USGS password', hide_input=True)
def usgsLogin(username, password):
    """Basic rewrite of usgs login cli with username and password prompt
    """
    api_key = api.login(username, password)
    print(api_key)

@click.command()
@click.option('--collection')
@click.option('--long')
@click.option('--lat')
@click.option('--radius', default = 2)
@click.option('--start_date', default = '1982-07-15')
@click.option('--end_date', default = today)
@click.option('--api_key')
def getSceneList(collection, long, lat, radius, end_date, start_date, api_key):
    if api_key is None:
        with open(KEY_FILE) as src:
            api_key = src.read()
    collection = makeEeFileName(collection)
    center_coords = {'long': long, 'lat': lat}
    ll, ur, lngs, lats = xyToBox(center_coords, radius)
    lst = querySceneLists(collection, ll, ur, start_date, end_date, api_key)
    print'\n'.join(lst)

@click.command()
@click.argument('scenelist', type=click.File('rb'))
@click.option('--collection', required=True)
@click.option('--proj', required = False)
@click.option('--resampling_method', default = 'bil')
@click.option('--xmin', required = False)
@click.option('--xmax', required = False)
@click.option('--ymin', required = False)
@click.option('--ymax', required = False)
@click.option('--username', prompt='USGS username')
@click.option('--password', prompt='USGS password', hide_input=True)
def orderFromList(username, password, scenelist, collection, proj, resampling_method):
    # TODO: investigate how to pass the products
    # Read scenelist (file) as a list
    with open(scenelist) as src:
        scene_list = src.read().splitlines()
    # Ensure that all items in the list belong to the right collection
    if not all(parseSceneId(scene)['sensor'] == collection.upper() for scene in scene_list):
        raise ValueError('Some elements of scenelist don\'t belong to the requested collection')
    # convert sensor to espa conventions
    collection = makeEspaFileName(collection)
    # start building json object for request
    json_class = jsonBuilder(collection, scene_list)
    # 
    if proj is not None:
        json_class.addProjection(proj = proj, resampling_method = resampling_method, center_coords = None)
        if all(item is not None for item in [xmin, xmax, ymin, ymax]):
            # resizing is optional but requires that the data be reprojected
            extent = {'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax}
            json_class.addResizeOption(extent)
    # Cary on with the request
    json = json_class.getDict()
    r = requests.post("https://espa.cr.usgs.gov/api/v0/order",\
        auth=(username, password), verify=False, json=json)
    if r.status_code != 200:
        raise ValueError('Something went wrong with the request')
    print r.text

# @click.command()
# @click.option('--name', required = False)
# def hello(name = 'loic'):
#     print 'Hello' + name


landespa.add_command(getSceneList)
landespa.add_command(usgsLogin)
# landespa.add_command(hello)

# Batch function:
    # Read file containing coordinates
    # For each line
        # ll, ul, lngs, lats = xyToBox()
        # scene_list_dict = querySceneLists()
        # for each item in scene_list_dict:
            # order_json = makeJson()
            # r = requests.post("https://espa.cr.usgs.gov/api/v0/order", auth=(user_name, password), verify=False, json=order_json)

