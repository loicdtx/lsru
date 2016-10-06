# Landsat-ESPA-util
*Interface to ESPA API for Landsat surface reflectance data ordering*

Before, downloading Landsat surface reflectance data for a given area meant:
- Manually query the sceneIDs on Earth Explorer
- Saving these lists of sceneIDs to text files
- Manually uploading these files to ESPA to place the order
- Downloading the processed data with a download manager

Now, thanks to [mapbox usgs](https://github.com/mapbox/usgs), the [espa API](https://github.com/USGS-EROS/espa-api), this utility, and [espa bulk downloader](https://github.com/USGS-EROS/espa-bulk-downloader), it can all be done from the command line. What a relief!!

## Why can't I just retrieve my Landsat data from Earth Explorer, Amazon or Google cloud?

You can but it will be top of atmosphere (TOA) radiance, not surface reflectance. If you aim to have a scientific use of the data, you probably want to have surface reflectance.

The critical part between TOA radiance and surface reflectance is the atmospheric correction. That means that surface reflectance data are corrected for atmospheric effects, therefore providing accurate measurements of the target's spectral properties.

Today (October 2016), there are a few ways to obtain Landsat surface reflectance data (All of them have been processed by LEDAPS, the reference high level Landsat processing tool):
1. By ordering them via the ESPA system
    - this is what this utility helps you to do
    - ESPA does on demand pre-processing of full scenes or (reprojected) subsets
    - A cloud mask (fmask) and vegetation indices can also be added to the order
1. By ordering them from Google Earth Engine
	- GEE has a 'vitual' surface reflectance collection (processed on the fly by LEDAPS) and is currently ingesting the entired ESPA archive.
1. By downloading TOA data from any source and processing with a local installation of LEDAPS
	- If you have a server and you're good with system administration, why not...