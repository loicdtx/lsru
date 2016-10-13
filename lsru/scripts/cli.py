from usgs import api
import csv
from lsru.lsru import getSceneList, orderList
from lsru import TODAY
import click
import requests

@click.group()
def lsru():
    pass

@click.command()
@click.option('--username', prompt='USGS username', help = 'Wait for prompt')
@click.option('--password', prompt='USGS password', help = 'Wait for prompt', hide_input=True)
def login(username, password):
    """Login to USGS Earth Explorer api
    
    Key expires after 1 hr. This is a basic rewrite of usgs login cli with username and password prompt.
    """
    api_key = api.login(username, password)
    print(api_key)

@click.command()
@click.option('--filename', required = False, help = 'Path to spatial vector file from which extent will be retrieved and used for the spatial query')
@click.option('--collection', help = 'Landsat collection to query from Earth Explorer (LT5, LE7 or LC8)')
@click.option('--long_0', type = float, help = 'Longitude of query point in decimal degrees')
@click.option('--lat_0', type = float, help = 'Latitude of query point in decimal degrees')
@click.option('--radius', default = 2, help = 'Square buffer radius in meters')
@click.option('--start_date', default = '1982-07-15', help = 'Start date yyyy-mm-dd, defaults to 1982-07-15')
@click.option('--end_date', default = TODAY, help = 'End date yyyy-mm-dd, defasults to today')
@click.option('--api_key', help = 'USGS API key, or run lsru login command prior to this one')
def query(collection, long_0, lat_0, radius, filename, end_date, start_date, api_key):
    """Perform a spatial query on the Earth Explorer API
    """
    lst = getSceneList(collection, long_0, lat_0, radius, filename, end_date, start_date, api_key)
    print'\n'.join(lst)

@click.command()
@click.argument('scenelist', type=click.File('rb'))
@click.option('--proj', help='Optional, projection to reproject to (Required if --resize flag is enabled)')
@click.option('--resampling_method', default = 'bil', help="One of bil (default), bil or cc")
@click.option('--resize/--no-resize', default = False, help="Enable for spatial subsetting, define spatial subset either via bounding box coordinates (xmin, xmax, ymin, ymax), or via center coord and radius (long_0, lat_0, radius), or spatial object (filename)") # THis is a flag
@click.option('--xmin', type = float, help="If --resize, west bound coordinate in DD")
@click.option('--xmax', type = float, help="If --resize, east bound coordinate in DD")
@click.option('--ymin', type = float, help="If --resize, south bound coordinate in DD")
@click.option('--ymax', type = float, help="If --resize, north bound coordinate in DD")
@click.option('--long_0', type = float, help="If --resize, center longitude in DD")
@click.option('--lat_0', type = float, help="If --resize, center latitude in DD")
@click.option('--radius', type = int, help="If --resize, square radius in meters")
@click.option('--filename', help="If --resize, path to spatial vector file from which extent will be retrieved and used")
@click.option('--username', prompt='USGS username', help = 'Wait for prompt')
@click.option('--password', prompt='USGS password', help = 'Wait for prompt', hide_input=True)
@click.option('--debug/--no-debug', default = False, help = 'If error, re-run with --debug and report the issue with the return')
def order(scenelist, proj, resampling_method, resize, xmin, xmax, ymin, ymax, long_0, lat_0, filename, radius, username, password, debug):
    """Place espa order for a list of Landsat scenes read from file

    File can be generated using the lsru query utility
    """
    # TODO: investigate how to pass the products
    # Read scenelist (filename) as a list
    # with open(scenelist) as src:
    scene_list = scenelist.read().splitlines()
    r = orderList(username, password, scene_list, proj, resampling_method, resize, xmin, xmax, ymin, ymax, long_0, lat_0, filename, radius, debug)
    print r.text

@click.command()
@click.option('--collection', help = 'Landsat collection to query from Earth Explorer (LT5, LE7 or LC8)')
@click.option('--long_0', type = float, help = 'Longitude of query point in decimal degrees')
@click.option('--lat_0', type = float, help = 'Latitude of query point in decimal degrees')
@click.option('--radius', default = 2, help = 'Square buffer radius in meters')
@click.option('--filename', required = False, help = 'Path to spatial vector file from which extent will be retrieved and used for the spatial query')
@click.option('--start_date', default = '1982-07-15', help = 'Start date yyyy-mm-dd')
@click.option('--end_date', default = TODAY, help = 'End date yyyy-mm-dd')
@click.option('--proj', help='Optional, projection to reproject to (Required if --resize flag is enabled)')
@click.option('--resampling_method', default = 'bil')
@click.option('--resize/--no-resize', default = False, help = "Enable for spatial subsetting")
@click.option('--xmin', type = float, help="If --resize, west bound coordinate in DD")
@click.option('--xmax', type = float, help="If --resize, east bound coordinate in DD")
@click.option('--ymin', type = float, help="If --resize, south bound coordinate in DD")
@click.option('--ymax', type = float, help="If --resize, north bound coordinate in DD")
@click.option('--api_key', help = 'USGS API key, or run usgslogin command prior to this one')
@click.option('--username', prompt='USGS username', help = 'Wait for prompt')
@click.option('--password', prompt='USGS password', help = 'Wait for prompt', hide_input=True)
@click.option('--debug/--no-debug', default = False, help = 'If error, re-run with --debug and report the issue with the return')
def sp_order(collection, long_0, lat_0, radius, filename, end_date, start_date, proj, resampling_method, resize, xmin, xmax, ymin, ymax, api_key, username, password, debug):
    """Query and order data for a given location
    """
    scenelist = getSceneList(collection, long_0, lat_0, radius, filename,\
        end_date, start_date, api_key)
    r = orderList(username, password, scenelist, proj, resampling_method, resize, xmin, xmax, ymin, ymax, long_0, lat_0, filename, radius, debug)
    if isinstance(r, requests.models.Response):
        print r.text
    else:
        print r

# username, password, scene_list, proj, resampling_method, resize, xmin = None,\
# xmax = None, ymin = None, ymax = None, long_0=None, lat_0=None, filename=None,\
# radius=None, debug=False

@click.command()
@click.argument('filename', type=click.File('rb'))
@click.option('--collection', help = 'Landsat collection to query from Earth Explorer (LT5, LE7 or LC8)')
@click.option('--radius', default = 100, help = 'Square buffer radius in meters')
@click.option('--start_date', default = '1982-07-15', help = 'Start date yyyy-mm-dd, defaults to 1982-07-15')
@click.option('--end_date', default = TODAY, help = 'End date yyyy-mm-dd, defasults to today')
@click.option('--proj', help = 'Optional, projection to reproject to (Required if --resize flag is enabled)')
@click.option('--resampling_method', default = 'bil', help = "One of bil (default), bil or cc")
@click.option('--resize/--no-resize', default = False, help = "Enable for spatial subsetting, --radius will be used if enabled") # THis is a flag
@click.option('--api_key', help = 'USGS API key, or run lsru login command prior to this one')
@click.option('--username', prompt='USGS username', help = 'Wait for prompt')
@click.option('--password', prompt='USGS password', help = 'Wait for prompt', hide_input=True)
@click.option('--debug/--no-debug', default = False, help = 'If error, re-run with --debug and report the issue with the return')
def order_batch(filename, collection, radius, start_date, end_date, proj, resampling_method, resize, api_key, username, password, debug):
    """Query and order data from a list of coordinates read from file
    """
    # with open(filename) as src:
    coord_list = [tuple(line) for line in csv.reader(filename)]
    for coord in coord_list:
        long_0 = float(coord[0])
        lat_0 = float(coord[1])
        scenelist = getSceneList(collection, long_0, lat_0, radius,filename = None,\
            end_date = end_date, start_date = start_date, api_key = api_key)
        r = orderList(username, password, scenelist, proj, resampling_method, resize,\
            long_0 = long_0, lat_0 = lat_0, radius = radius, debug = debug)
        if isinstance(r, requests.models.Response):
            print r.text
        else:
            print r
    print "Order complete"

lsru.add_command(query)
lsru.add_command(login)
lsru.add_command(order)
lsru.add_command(sp_order)
lsru.add_command(order_batch)

