"""SAR-FLOOD MAPPING USING A CHANGE DETECTION APPROACH

  This script use SAR Sentinel-1 images to generate a flood extent map. A
  change detection approach was chosen, where a before- and after-flood
  event image will be compared. The dataset available in the Earth Engine
  Data Catalog includes the following preprocessing steps: Thermal-Noise
  Removal, Radiometric calibration, and Terrain-correction.
"""

import ee

# Earth Engine Viz Parameters
geoviz_app = {
    "s1_img": {"min": -25, "max": 0},
    "diff_s1": {"min": 0, "max": 2},
    "flood": {"palette": "0000FF"},
    "populationCountVis": {
        "min": 0, "max": 200.0,
        "palette": ['060606', '337663', '337663', 'ffffff']
    },
    "populationExposedVis": {
        "min": 0, "max": 200.0, 
        "palette": ['yellow', 'orange', 'red']
    },
    "LCVis": {
        "min": 1.0, "max": 17.0,
        "palette": [
            '05450a', '086a10', '54a708', '78d203',
            '009900', 'c6b044', 'dcd159', 'dade48',
            'fbff13', 'b6ff05', '27ff87', 'c24f44',
            'a5a5a5', 'ff6d4c', '69fff8', 'f9ffa4',
            '1c0dff'
        ]
    },
    "croplandVis": {"min": 0, "max": 14.0, "palette": ['30b21c']},
    "urbanVis": {"min": 0, "max": 13.0, "palette": ['grey']}
}


# Display basemap
def display(dict_db):
    """ Display a basic Earth Engine map
    Returns:
        str: earthengine tiles googleapis
    """

    # S1 before flood
    s1_bf = ee.Image.visualize(dict_db["before_flood"], **geoviz_app["s1_img"])
    s1_bf_id = ee.data.getMapId({"image": s1_bf})["tile_fetcher"].url_format

    # S1 after flood
    s1_af = ee.Image.visualize(dict_db["after_flood"], **geoviz_app["s1_img"])
    s1_af_id = ee.data.getMapId({"image": s1_af})["tile_fetcher"].url_format

    # Flood results
    s1_fresults = ee.Image.visualize(dict_db["flood_results"], **geoviz_app["flood"])
    s1_fresults_id = ee.data.getMapId({"image": s1_fresults})["tile_fetcher"].url_format
    
    layer_to_display = {
        "before_flood": s1_bf_id,
        "after_flood": s1_af_id,
        "s1_fresults_id": s1_fresults_id
    }
    return layer_to_display

# Extract date from meta data
def dates(imgcol):
    range = imgcol.reduceColumns(ee.Reducer.minMax(), ["system:time_start"])
    ee_min = ee.Date(range.get('min')).format('YYYY-MM-dd').getInfo()
    ee_max = ee.Date(range.get('max')).format('YYYY-MM-dd').getInfo()
    printed = "from %s to %s" % (ee_min, ee_max)
    return printed


def db_creator(base_period , flood_period, geometry, polarization="VH",
               pass_direction="DESCENDING", quiet=False):

    # rename selected geometry feature
    aoi = ee.FeatureCollection(geometry)

    # Load and filter Sentinel-1 GRD data by predefined parameters
    collection = ee.ImageCollection("COPERNICUS/S1_GRD")\
                  .filter(ee.Filter.eq("instrumentMode", "IW"))\
                  .filter(ee.Filter.listContains("transmitterReceiverPolarisation", polarization))\
                  .filter(ee.Filter.eq("orbitProperties_pass",pass_direction))\
                  .filter(ee.Filter.eq("resolution_meters",10)) \
                  .filterBounds(aoi)\
                  .select(polarization)
    # .filter(ee.Filter.eq('relativeOrbitNumber_start', relative_orbit)) \

    # Select images by predefined dates
    before_collection = collection.filterDate(base_period[0], base_period[1])
    after_collection = collection.filterDate(flood_period[0], flood_period[1])

    if quiet:
        # print dates of before images to console
        before_count = before_collection.size().getInfo()
        print("Tiles selected: Before Flood (%s) \n %s" % (before_count, dates(before_collection)))

        # print dates of after images to console
        after_count = before_collection.size().getInfo()
        print("Tiles selected: After Flood  (%s) \n %s" % (after_count, dates(after_collection)))

    # Create a mosaic of selected tiles and clip to study area
    before = before_collection.mosaic().clip(aoi)
    after = after_collection.mosaic().clip(aoi)

    # Apply reduce the radar speckle by smoothing
    smoothing_radius = 50
    before_filtered = before.focal_mean(smoothing_radius, "circle", "meters")
    after_filtered = after.focal_mean(smoothing_radius, "circle", "meters")
    dict_preprocessing = dict(before_flood=before_filtered,
                              after_flood=after_filtered,
                              base_period=base_period,
                              flood_period=flood_period,
                              aoi=aoi,
                              polarization=polarization)
    return dict_preprocessing


def flood_estimation(dict_db, difference_threshold=1.25, stats=True):

    before_filtered = dict_db["before_flood"]
    after_filtered = dict_db["after_flood"]
    polarization = dict_db["polarization"]
    aoi = dict_db["aoi"]

    # Calculate the difference between the before and after images
    difference = after_filtered.divide(before_filtered)

    # Apply the predefined difference-threshold and create the flood extent mask
    threshold = difference_threshold
    difference_binary = difference.gt(threshold)

    # Refine flood result using additional datasets
    #    Include JRC layer on surface water seasonality to mask flood pixels from areas
    #    of "permanent" water (where there is water > 10 months of the year)
    swater = ee.Image('JRC/GSW1_0/GlobalSurfaceWater').select('seasonality')
    swater_mask = swater.gte(10).updateMask(swater.gte(10))

    # Flooded layer where perennial water bodies (water > 10 mo/yr) is assigned a 0 value
    flooded_mask = difference_binary.where(swater_mask, 0)
    # final flooded area without pixels in perennial waterbodies
    flooded = flooded_mask.updateMask(flooded_mask)

    # Compute connectivity of pixels to eliminate those connected to 8 or fewer neighbours
    # This operation reduces noise of the flood extent product
    connections = flooded.connectedPixelCount()
    flooded = flooded.updateMask(connections.gte(8))

    # Mask out areas with more than 5 percent slope using a Digital Elevation Model    
    DEM = ee.Image('WWF/HydroSHEDS/03VFDEM')
    terrain = ee.Algorithms.Terrain(DEM)
    slope = terrain.select('slope')
    flooded = flooded.updateMask(slope.lt(5))
    
    dict_db.update({"flood_results": flooded}) # add flood mask results to the db

    if stats:
        # Calculate flood extent area
        # Create a raster layer containing the area information of each pixel
        flood_pixelarea = flooded.select(polarization).multiply(ee.Image.pixelArea())

        # Sum the areas of flooded pixels
        # default is set to 'bestEffort: true' in order to reduce compuation time, for a more
        # accurate result set bestEffort to false and increase 'maxPixels'.
        flood_stats = flood_pixelarea.reduceRegion(
          reducer=ee.Reducer.sum(),
          geometry=aoi,
          scale=10, # native resolution
          bestEffort=True
        )

        # Convert the flood extent to hectares (area calculations are originally given in meters)
        flood_area_ha = flood_stats\
          .getNumber(polarization)\
          .divide(10000)\
          .round() \
          .getInfo()
        dict_db.update({"flood_area_stats":flood_area_ha}) # add flood stats results to the db
    return dict_db