import requests
import os
from usgs import api
from datetime import datetime
from landespa.util import querySceneLists, parseSceneId, jsonBuilder, makeEeFileName, makeEspaFileName
from landespa.util import extent_geo, orderList, getSceneList
import click

today = str(datetime.today().date())

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
@click.option('--file', required = False, help = 'Path to spatial vector file from which extent will be retrieved and used for the spatial query')
@click.option('--collection', help = 'Landsat collection to query from Earth Explorer (LT5, LE7 or LC8)')
@click.option('--long_0', help = 'Longitude of query point in decimal degrees')
@click.option('--lat_0', help = 'Latitude of query point in decimal degrees')
@click.option('--radius', default = 2, help = 'Square buffer radius in meters')
@click.option('--start_date', default = '1982-07-15', help = 'Start date yyyy-mm-dd')
@click.option('--end_date', default = today, help = 'End date yyyy-mm-dd')
@click.option('--api_key', help = 'USGS API key, or run usgslogin command prior to this one')
def query(collection, long_0, lat_0, radius, file, end_date, start_date, api_key):
    lst = getSceneList(collection, long_0, lat_0, radius, file, end_date, start_date, api_key)
    print'\n'.join(lst)

@click.command()
@click.argument('scenelist', type=click.File('rb'))
@click.option('--proj')
@click.option('--resampling_method', default = 'bil')
@click.option('--resize/--no-resize', default = False) # THis is a flag
@click.option('--xmin')
@click.option('--xmax')
@click.option('--ymin')
@click.option('--ymax')
@click.option('--long_0')
@click.option('--lat_0')
@click.option('--radius')
@click.option('--file')
@click.option('--username', prompt='USGS username')
@click.option('--password', prompt='USGS password', hide_input=True)
def orderFromList(scenelist, proj, resampling_method, resize, xmin, xmax, ymin, ymax, long_0, lat_0, file, radius, username, password):
    # TODO: investigate how to pass the products
    # Read scenelist (file) as a list
    with open(scenelist) as src:
        scene_list = src.read().splitlines()
    r = orderList(scenelist, proj, resampling_method, resize, xmin, xmax, ymin, ymax, long_0, lat_0, file, radius, username, password)
    print r.text

@click.command()
@click.option('--collection', help = 'Landsat collection to query from Earth Explorer (LT5, LE7 or LC8)')
@click.option('--long_0', type = float, help = 'Longitude of query point in decimal degrees')
@click.option('--lat_0', type = float, help = 'Latitude of query point in decimal degrees')
@click.option('--radius', default = 2, help = 'Square buffer radius in meters')
@click.option('--file', required = False, help = 'Path to spatial vector file from which extent will be retrieved and used for the spatial query')
@click.option('--start_date', default = '1982-07-15', help = 'Start date yyyy-mm-dd')
@click.option('--end_date', default = today, help = 'End date yyyy-mm-dd')
@click.option('--proj')
@click.option('--resampling_method', default = 'bil')
@click.option('--resize/--no-resize', default = False) # THis is a flag
@click.option('--xmin', type = float)
@click.option('--xmax', type = float)
@click.option('--ymin', type = float)
@click.option('--ymax', type = float)
@click.option('--api_key', help = 'USGS API key, or run usgslogin command prior to this one')
@click.option('--username', prompt='USGS username')
@click.option('--password', prompt='USGS password', hide_input=True)
def orderSpatial(collection, long_0, lat_0, radius, file, end_date, start_date, proj, resampling_method, resize, xmin, xmax, ymin, ymax, api_key, username, password):
    scenelist = getSceneList(collection, long_0, lat_0, radius, file, end_date, start_date, api_key)
    r = orderList(scenelist, proj, resampling_method, resize, xmin, xmax, ymin, ymax, long_0, lat_0, file, radius, username, password)
    print r.text

landespa.add_command(query)
landespa.add_command(usgsLogin)
landespa.add_command(orderFromList)
landespa.add_command(orderSpatial)
# landespa.add_command(hello)
