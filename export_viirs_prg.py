import ee
ee.Initialize()

from datetime import datetime

ROIs = {
    'BC': ee.Geometry.Polygon(
            [[[-130.06011633534416, 55.743795953925485],
            [-130.06011633534416, 47.477843024642524],
            [-112.08648352284416, 47.477843024642524],
            [-112.08648352284416, 55.743795953925485]]]),

    'EU': 0,

    'CA': ee.Geometry.Polygon(
        [[[-124.57444768727125, 42.07370311787262],
          [-124.57444768727125, 32.37061559426462],
          [-114.11546331227126, 32.37061559426462],
          [-114.11546331227126, 42.07370311787262]]]),
}

# /* VIIRS Active Fire */    
def export_daily_viirs_progression(prg_roi, asset_name="bc_virrs_prg", start_date=None, end_date=None):
    base_AF_SUOMI_VIIRS = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/SUOMI_VIIRS_C2_Global_Archived_2021")
    base_AF_J1_VIIRS = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/J1_VIIRS_C2_Global_Archived_2021")
    AF_BASE = base_AF_SUOMI_VIIRS.merge(base_AF_J1_VIIRS)

    AF_SUOMI_VIIRS = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/SUOMI_VIIRS_C2_Global_7d")
    AF_J1_VIIRS = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/J1_VIIRS_C2_Global_7d")
    AF_MODIS = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/MODIS_C6_1_Global_7d")
        
    def set_buffer(pnt): return pnt.buffer(ee.Number(500).divide(2)).bounds()
    def set_julian_day(pnt): return pnt.set("julian_day", ee.Date(pnt.get("ACQ_DATE")).getRelative('day', 'year'))

    viirs_af = (AF_SUOMI_VIIRS.merge(AF_J1_VIIRS).merge(AF_MODIS).filterBounds(prg_roi)
                        .merge(AF_BASE.filterBounds(prg_roi))
                        .map(set_julian_day)
        )
                    
    #   // print("before filtering: " + viirs_af.size().getInfo())
    if start_date is None: start_date = "2021-05-01"
    if end_date is None: end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S").split("T")[0]
    viirs_af = (viirs_af
                    .filter(ee.Filter.gte("julian_day", ee.Date(start_date).getRelative('day', 'year')))
                    .filter(ee.Filter.lte("julian_day", ee.Date(end_date).getRelative('day', 'year')))
                )
    #   // print("after filtering: " + viirs_af.size().getInfo())     
                        
    min_max = viirs_af.reduceColumns(ee.Reducer.percentile([2, 98], ['min', 'max']), ['julian_day'])
    min = min_max.get('min').getInfo()
    max = min_max.get('max').getInfo()
                        
    viirs_prg = viirs_af.map(set_buffer).reduceToImage(["julian_day"], ee.Reducer.first()).rename('prg')
    viirs_prg = ee.Image(viirs_prg.setMulti({'min': min, 'max': max}))

    task = ee.batch.Export.image.toAsset(
        image=viirs_prg,
        description= asset_name, 
        assetId=f"users/omegazhangpzh/NRT_AF/{asset_name}",
        region=prg_roi,
        scale=500 ,
        crs="EPSG:4326", 
        maxPixels=1e10,
        shardSize=1024
    )

    task.start()


    # ee.batch.Export.image.toCloudStorage(
    #     image = viirs_prg,
    #     description = "export to cloud", 
    #     bucket = "sar4wildfire", 
    #     fileNamePrefix = 'bc_viirs_prg', 
    #     region = prg_roi, 
    #     scale = 100, 
    #     crs = "EPSG:4326", 
    #     fileFormat = "GeoTIFF", 
    #     formatOptions = {
    #         "cloudOptimized": True
    #     }
    # )
  
#   // set_buffer_1km = function(pnt){return pnt.buffer(ee.Number(1000).divide(2)).bounds()}
#   // burned_area = viirs_af.map(set_buffer_1km).reduceToImage(["julian_day"] ee.Reducer.first()).rename('prg')
  
#   return {
#     progression: viirs_prg 
#     julian_min: min 
#     julian_max: max 
#     // burned_area: burned_area
#   }

if __name__ == "__main__":
    export_daily_viirs_progression(prg_roi=ROIs['BC'], asset_name="bc_virrs_prg", start_date="2021-06-20")
    export_daily_viirs_progression(prg_roi=ROIs['CA'], asset_name="ca_virrs_prg", start_date="2021-07-01")  