import requests
from datetime import datetime
from landespa.util import xyToBox, querySceneLists, parseSceneId, jsonBuilder
import click


today = str(datetime.today().date())


@click.group()
def landespa():
    pass

@click.command()
@click.argument('collection', nargs = 1)
@click.argument('long', nargs = 1)
@click.argument('lat', nargs = 1)
@click.option('--radius', default = 2)
@click.option('--start_date', default = '1982-07-15')
@click.option('--end_date', default = today)
@click.option('--api_key')
def sceneListFromPoint(collection, long, lat, radius, end_date, start_date, api_key):
	center_coords = {'long': long, 'lat': lat}
	ll, ur, lngs, lats = xyToBox(center_coords, radius)
	lst = querySceneLists(collection, ll, ur, start_date, end_date, api_key)
	print'\n'.join(lst)



landespa.add_command(sceneListFromPoint)

# Batch function:
    # Read file containing coordinates
    # For each line
        # ll, ul, lngs, lats = xyToBox()
        # scene_list_dict = querySceneLists()
        # for each item in scene_list_dict:
            # order_json = makeJson()
            # r = requests.post("https://espa.cr.usgs.gov/api/v0/order", auth=(user_name, password), verify=False, json=order_json)

