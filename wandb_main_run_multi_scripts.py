import os, time                                                                       
from multiprocessing import Pool                                                
                                                                                                                                                                                                                                                                                             
def run_process(process):   
    if 'virrs' in process: 
        os.system('C:/Anaconda3/envs/ee/python.exe {}'.format(process))   
    else:                                                        
        os.system('python {}'.format(process))                                       
                                                                                
if __name__ == "__main__":
    
    """ S1 """
    # config = "roi_url=inputs\S1_vSplit_BC_ROI1.geojson satellite=sentinel1 start_date=2021-07-30 end_date=2021-07-31"
    # config = "roi_url=inputs\S1_vSplit_BC_ROI1.geojson satellite=sentinel1"
    # config = "roi_url=inputs/S1_vSplit_BC_ROI1.geojson satellite=sentinel1 start_date=2021-07-30 end_date=2021-07-31"
    # config = "roi_url=inputs/S1_vSplit_BC_ROI1.geojson satellite=sentinel1"
    config = "roi_url=inputs/S1_split_US.geojson satellite=sentinel1"


    # config = "roi_url=inputs\S1_vSplit_BC_ROI2.geojson satellite=sentinel1"

    """ S2 """
    # config = "roi_url=inputs/S2_East_CA.geojson satellite=sentinel2"
    # config = "roi_url=inputs/S2_BC_ALB_fireCenter.geojson satellite=sentinel2 cloudcoverpercentage=100"
    config = "roi_url=inputs/S2_BC_small.geojson satellite=sentinel2"

    # independent processes
    processes = (
            # 'update_active_fire.py', 
            # 'update_viirs_nrt.py',
            f'wandb_sentinel_query_download.py {config}',
            f'wandb_update_sentinel_for_gee.py {config}'
        )

    # dependent processes
    other = ()

    # run every 2 hours
    while(True):
        
        pool = Pool(processes=len(processes)+len(other)) 
        pool.map(run_process, processes)
        pool.map(run_process, other)

        time.sleep(10*60)
