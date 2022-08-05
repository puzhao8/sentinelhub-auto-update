import datetime
import json
import os

import requests


class LaadsClient:

    def __init__(self):
        self.laads_query_api_link = 'https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/details'
        self.download_base_link = 'https://ladsweb.modaps.eosdis.nasa.gov'
        self.header = {
            "X-Requested-With": "XMLHttpRequest",
            'Authorization': 'Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYzMzk0NzU0NTphZmRlYWY2MjE2ODg0MjQ5MTEzNmE3MTE4MzZkOWYxYjg3MWQzNWMz'}

    def query_filelist_with_date_range_and_area_of_interest(self, date, products_id, data_path='data/VNPL1', collection_id='5110', julian_day='182'):
        # products_id = ['VNP02IMG', 'VNP03IMG']
        # print(date)
        for i in range(len(products_id)):
            product_id = products_id[i]
            download_link = self.laads_query_api_link \
                            + '?products='+product_id \
                            + '&collections='+collection_id \
                            + '&archiveSets='+collection_id \
                            + '&temporalRanges=' + date
            
            response = requests.get(download_link, headers=self.header)
            if response.status_code != 200:
                raise ConnectionRefusedError
            else:
                json_path = os.path.join(data_path, julian_day)
                if not os.path.exists(json_path):
                    os.makedirs(json_path)
                with open(os.path.join(json_path, date + '_'+product_id+'.json'), 'wb') as outf:
                    outf.write(response.content)
                print('New ' + product_id +' file list for day '+date+' created')

    def download_files_to_local_based_on_filelist(self, date, products_id = ['VNP02IMG', 'VNP03IMG'], collection_id='5110', data_path='data/VNPL1', julian_day='182'):
        for i in range(len(products_id)):
            hh_list_na = ['08', '09', '10', '11', '12', '13']
            vv_list_na = ['02', '03', '04', '05']

            hh_list_eu = ['17', '18', '19', '20', '21']
            vv_list_eu = ['02', '03', '04', '05']

            hh_list_na = hh_list_eu
            vv_list_na = vv_list_eu

            product_id = products_id[i]
            vnp_json = open(os.path.join(data_path, julian_day, date + '_'+product_id+'.json'), )
            vnp_list = json.load(vnp_json)['content']
            vnp_list = [file for file in vnp_list if file['archiveSets']==int(collection_id)]
            print('There are ' + str(vnp_list.__len__()) + ' ' + product_id +' files to download in total.')
            for vnp_file in vnp_list:
                vnp_name = vnp_file['name']
                h_coor = vnp_name.split('.')[2][1:3]
                v_coor = vnp_name.split('.')[2][4:]
                if not ((h_coor in hh_list_na and v_coor in vv_list_na) or (h_coor in hh_list_eu and v_coor in vv_list_eu)):
                    continue
                time_captured = vnp_name.split('.')[2]
                vnp_link = vnp_file['downloadsLink']
                # Keep a clean directory before downloading
                # if not os.path.exists(data_path + '/' + julian_day + '/' + time_captured):
                #     os.mkdir(data_path + '/' + julian_day + '/' + time_captured)

                if not os.path.exists(data_path + '/' + julian_day + '/' + vnp_name):
                    print("Downloading netCDF files " + vnp_name.split('.')[1] + vnp_name.split('.')[
                        2] + " from Remote server")
                    # shutil.rmtree(data_path + '/' + date + '/' + time_captured)
                    wget_command_vnp = "wget " + vnp_link +" --header X-Requested-With:XMLHttpRequest" + " --header \"Authorization: Bearer emhhb3l1dGltOmVtaGhiM2wxZEdsdFFHZHRZV2xzTG1OdmJRPT06MTYzMzk0NzU0NTphZmRlYWY2MjE2ODg0MjQ5MTEzNmE3MTE4MzZkOWYxYjg3MWQzNWMz\" -P " + data_path + '/' + julian_day
                    os.system(wget_command_vnp)

if __name__ == '__main__':
    date = '2022-07-01'
    date_ndays = (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.datetime.strptime(date[:4] + '-01-01', '%Y-%m-%d')).days + 1
    laads_client = LaadsClient()

    # # VIIRS
    # laads_client.query_filelist_with_date_range_and_area_of_interest(date, products_id=['VNP09GA'], collection_id='5000', data_path='../data/data/VIIRS_NRT/5000/VNP09GA_NRT/2022', julian_day=str(date_ndays))
    # laads_client.download_files_to_local_based_on_filelist(date, products_id=['VNP09GA'], collection_id='5000', data_path='../data/data/VIIRS_NRT/5000/VNP09GA_NRT/2022', julian_day=str(date_ndays))

    # MODIS
    laads_client.query_filelist_with_date_range_and_area_of_interest(date, products_id=['MOD09GA'], collection_id='61', data_path='../data/data/MODIS_NRT/61/MOD09GA/2022', julian_day=str(date_ndays))
    laads_client.download_files_to_local_based_on_filelist(date, products_id=['MOD09GA'], collection_id='61', data_path='../data/data/MODIS_NRT/61/MOD09GA/2022', julian_day=str(date_ndays))