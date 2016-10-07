import requests
import os
from usgs import api
from datetime import datetime
from landespa.util import xyToBox, querySceneLists, parseSceneId, jsonBuilder, makeEeFileName
import click


today = str(datetime.today().date())
KEY_FILE = os.path.expanduser('~/.usgs')


@click.group()
def landespa():
    pass

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
@click.option('--username', prompt='USGS username')
@click.option('--password', prompt='USGS password', hide_input=True)
def usgsLogin(username, password):
    """Basic rewrite of usgs login cli with username and password prompt
    """
    api_key = api.login(username, password)
    print(api_key)



landespa.add_command(getSceneList)
landespa.add_command(usgsLogin)

# Batch function:
    # Read file containing coordinates
    # For each line
        # ll, ul, lngs, lats = xyToBox()
        # scene_list_dict = querySceneLists()
        # for each item in scene_list_dict:
            # order_json = makeJson()
            # r = requests.post("https://espa.cr.usgs.gov/api/v0/order", auth=(user_name, password), verify=False, json=order_json)

