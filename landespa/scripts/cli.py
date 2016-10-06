import pyproj
from shapely import geometry
from usgs import soap, api
import requests
from pprint import pprint
import click

# Parameter
# Coordinates of a point (flux tower) in decimal degrees
center_long = 12
center_lat = 45
start_date='2015-04-01'
end_date='2016-05-01'
# radius in meters, used to defined the extent around the supplied origin
radius = 2000
user_name = 'dutrieux'
password = 'passwd'
# Get your own api key using "usgs login usgs_username usgs_password" directly from the command line
api_key = '233009bd81ee4aa3b48169a7c1dd3a78'




@click.group()
def landespa():
    pass

@click.command()
def 

def main():
    # Read file containing coordinates
    # For each line
        # ll, ul, lngs, lats = xyToBox()
        # scene_list_dict = querySceneLists()
        # for each item in scene_list_dict:
            # order_json = makeJson()
            # r = requests.post("https://espa.cr.usgs.gov/api/v0/order", auth=(user_name, password), verify=False, json=order_json)


if __name__ == '__main__':
    main()