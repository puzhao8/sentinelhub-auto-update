from tkinter import Scale
import os
import ee
ee.Initialize()


AF_SV_yr = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/SUOMI_VIIRS_C2_Global_Archived_2022")
AF_J1_yr = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/J1_VIIRS_C2_Global_Archived_2022")
AF_MOD_yr = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/MODIS_C6_1_Global_Archived_2022")

AF_SV_7d = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/SUOMI_VIIRS_C2_Global_7d")
AF_J1_7d = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/J1_VIIRS_C2_Global_7d")
AF_MOD_7d = ee.FeatureCollection("users/omegazhangpzh/NRT_AF/MODIS_C6_1_Global_7d")

AF_DICT = {
    'VIIRS': AF_SV_yr.merge(AF_J1_yr),
    'MODIS': AF_MOD_yr
}
    
def set_buffer(pnt): return pnt.buffer(ee.Number(500).divide(2)).bounds()
def set_julian_day(pnt): return pnt.set("julian_day", ee.Date(pnt.get("ACQ_DATE")).getRelative('day', 'year'))


# /* VIIRS Active Fire */
def export_daily_progression(source, prg_roi, start_date, end_date, asset_name):
    
    viirs_af = (
        AF_DICT[source]
            .filterBounds(prg_roi)
            .map(set_julian_day)
            .filter(ee.Filter.gte("julian_day", ee.Date(start_date).getRelative('day', 'year')))
            .filter(ee.Filter.lte("julian_day", ee.Date(end_date).getRelative('day', 'year')))
    )   
                        
    min_max = viirs_af.reduceColumns(ee.Reducer.percentile([2, 98], ['min', 'max']), ['julian_day'])
    min = min_max.get('min').getInfo()
    max = min_max.get('max').getInfo()
                        
    viirs_prg = viirs_af.map(set_buffer).reduceToImage(["julian_day"], ee.Reducer.first()).rename('prg')
    viirs_prg = ee.Image(viirs_prg.setMulti({'min': min, 'max': max}))

    asset_id = "users/omegazhangpzh/NRT_AF/" + asset_name
    rm_cmd = "earthengine rm " + asset_id
    os.system(rm_cmd)

    print("update: users/omegazhangpzh/NRT_AF/" + asset_name)
    task = ee.batch.Export.image.toAsset(
        image= viirs_prg,
        description= asset_name, 
        assetId= asset_id,
        region= prg_roi,
        scale= 500,
        crs= "EPSG:4326", 
        maxPixels= 1e10,
        shardSize= 1024
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
  

if __name__ == "__main__":

    ''' European Union (EU) '''
    EU_roi = ee.Geometry.Rectangle([
        -12.760569586626564,27.78277291262683,
        51.926930413373434,63.909391052873566
    ])

    ''' North America (NA) '''
    NA_roi = ee.Geometry.Rectangle([
        # -130.68110818541575,31.587311832883508,
        # -101.67720193541574,59.58406726407946
        -166.56718750000002,28.134679454322296,
        -71.99687500000002,72.01453861169225
    ])

    start_date = "2022-06-01"
    end_date = "2022-08-30"

    for source in ['VIIRS', 'MODIS']:
        export_daily_progression(source, EU_roi, start_date, end_date, source+"_PRG_2022_EU")
        export_daily_progression(source, NA_roi, start_date, end_date, source+"_PRG_2022_NA")
        