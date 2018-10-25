Order data using a polygon
==========================

The following example details the steps to place a pre-processing order of scenes intersecting with a polygon. 
Such task requires a little bit of boilerplate code since the Usgs API requires an extent and not a , but thanks to ``shapely`` and some additional utilities provided by ``lsru`` can be done with a few lines of code. 
The steps are roughly to:

- Read the feature (e.g. using ``fiona`` or directly from a geojson file with ``json``)
- Compute the bounding box of the feature
- Query scenes intersecting with the bounding box to the Usgs API
- Filter out scenes that do not intersect with the geometry
- Place the pre-processing order to Espa

To run this script, we'll need shapely, and some utils to manipulate geojson geometries provided by lsru. You may need fiona as well in case you need to read a feature from a geospatial vector file (shapefile, geopackage, etc)


from datetime import datetime

from shapely.geometry import shape

from lsru import Usgs, Espa, Order
from lsru.utils import bounds, geom_from_metadata

For the present example, we'll use the following feature, which roughly corresponds to the contours of the state of Baja California Sur in Mexico. 


feature = {'geometry': {'coordinates': [[[-114.192, 27.975],
                                         [-114.456, 27.8],
                                         [-115.093, 27.878],
                                         [-114.543, 27.313],
                                         [-113.928, 26.922],
                                         [-113.423, 26.844],
                                         [-112.72, 26.412],
                                         [-112.148, 25.741],
                                         [-112.324, 24.827],
                                         [-111.687, 24.467],
                                         [-110.984, 24.147],
                                         [-110.72, 23.725],
                                         [-110.281, 23.504],
                                         [-110.061, 22.877],
                                         [-109.446, 23.06],
                                         [-109.424, 23.423],
                                         [-110.259, 24.347],
                                         [-110.347, 24.187],
                                         [-110.61, 24.327],
                                         [-110.588, 24.707],
                                         [-111.445, 26.215],
                                         [-112.654, 27.684],
                                         [-112.961, 28.053],
                                         [-114.192, 27.975]]],
           'type': 'Polygon'},
           'properties': {},
           'type': 'Feature'}

# Generate the bounding box of the geometry used for the spatial query
bbox = bounds(feature['geometry'])

# Instantiate Usgs class and login
usgs = Usgs()
usgs.login()
collection = usgs.get_collection_name(8)

# Query for records of Landsat 8 intersecting with the spatio-temporal window
meta_list = usgs.search(collection=collection, bbox=bbox,
                        begin=datetime(2018, 1, 1), end=datetime(2018, 2, 28),
                        max_cloud_cover=30)
print(len(meta_list))
# 52
# Because we queried the data using the extent, it is highly probable that some scenes do not intersect with the initial geometry but only with its extent. We can therefore filter the list of scene metadata by testing for intersection between the scene bounds and the geometry. This is done using shapely
region_geom = shape(feature['geometry'])
meta_list = [x for x in meta_list if
             shape(geom_from_metadata(x)).intersects(region_geom)]

print(len(meta_list))
# 27
# The amount of element has reduced by half compared to the total API hits and we are now sure to have retained only scenes that actually intersect with the initial geometry

# We can now proceed to preparing the scene list for placing the order to espa
scene_list = [x['displayId'] for x in meta_list]
espa = Espa()
order_meta = espa.order(scene_list,
                        products=['pixel_qa', 'sr_ndmi'])

# We can then instantiate an Order class to track the status of the order and eventually download it once processing is completed
order = Order(order_meta['orderid'])
print(order.status)


