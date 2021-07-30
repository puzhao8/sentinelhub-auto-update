import os, time  
from datetime import datetime                                                                     
from multiprocessing import Pool                                                
                                                                                                                                                                                                                                                                                             
def run_process(process):   
    if 'virrs' in process: 
        os.system('C:/Anaconda3/envs/ee/python.exe {}'.format(process))   
    else:                                                        
        os.system('python {}'.format(process))                                       
                                                                                
if __name__ == "__main__":
    
    # independent processes
    processes = (
            # 'update_active_fire.py', 
            # 'update_viirs_nrt.py',
            'sentinel_query_download.py',
            'update_sentinel_for_gee.py'
        )

    # dependent processes
    other = ()

    # run every 2 hours
    while(True):

        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        hour = now.split("T")[1]

        if('11:00:00' == hour):
            print(f"===> updated on {now}")
        
        pool = Pool(processes=len(processes)+len(other)) 
        pool.map(run_process, processes)
        pool.map(run_process, other)

        # time.sleep(30*60)
