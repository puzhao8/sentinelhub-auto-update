"# sentinelhub-auto-query" 
This project is used to reduce the delay of VIIRS, Sentinel-1, and Sentinel-2 updating in Google Earth Engine (GEE), by downloading data from ESA Open Access Hub (https://scihub.copernicus.eu/dhus/#/home), processing locally, and uploading them as ee.ImageCollection asset in GEE.


# Config Environment
## 1. Install anaconda
https://docs.anaconda.com/anaconda/install/index.html

## 2. Install ESA SNAP Desktop Software (for Sentinel-2 and Sentinel-1 only)
https://step.esa.int/main/download/snap-download/
choose python 3.6 as interpreter

### 2.1 config snappy (ESA SNAP python library)
snappy only supports python 2.7 and python 3.6 (python 3.6 is recommended.)
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface

### 2.2 for windows
$ cd C:\SNAP\bin
$ snap-conf C:\Anaconda3\envs\snap\python G:\PyProjects\sentinelhub-auto-query\outputs\

copy generated snappy folder into envs you would like to use:
C:\Anaconda3\envs\snap\Lib\site-packages\

## 3. gcloud insallation and initializing
https://cloud.google.com/sdk/docs/install </br>
https://cloud.google.com/sdk/docs/initializing

``` bash
gcloud init
gcloud auth login
gcloud config set project [project-name]
```

# How to run:

``` bash 
conda activate snap
cd path/to/project
```

## update recent 7 days' active fire points 
``` bash
python update_active_fire_recent7days.py
```

## update archived active fire points older than 7 days
``` bash
python update_active_fire_archived.py
```

## update modis and viirs NRT data
``` bash
python update_modis_nrt.py
```
``` bash
python update_viirs_nrt.py
```

## update Sentinel-2 and Sentinel-1 from Sentinel Hub
### Solution 1: download and update through airflow like platform

Query and download data from Sentinel Open Hub:

``` bash
python wandb_sentinel_query_download.py --config-name=config_name
```

Preprocess, upload, and update in GEE assets:
``` bash
python wandb_update_sentinel_for_gee.py --config-name=config_name
```

More parameters can be updated in config/main.yaml, or config/satellite/sentinel1.yaml. Or specify as follows:
``` bash
python wandb_sentinel_query_download.py --config-name=config_name \
                                            eeUser=xxxxxxx \
                                            roi_url=inputs/xx.geojson \
                                            satellite=sentinel1 \
                                            start_date='2023-05-10' \
                                            end_date='2023-06-01' \
                                            gs_dir: gs://sar4wildfire/Sentinel1

```


### Solution 2: download and update in parallel through multiprocessing
``` bash
python wandb_main_run_multi_scripts.py
```

This command line will run sentinel_query_download.py and update_sentinel_for_gee.py in parallel, and you can change the variable config in wandb_main_run_multi_scripts.py:

For Sentinel-1, the default start_date is the day before today, and end_date is the day after today.
``` python
config = "roi_url=inputs/S1_split_US.geojson satellite=sentinel1"
```
For Sentinel-2, you can change it into 
``` python
config = "roi_url=inputs/S2_BC_ALB_fireCenter.geojson satellite=sentinel2 cloudcoverpercentage=100"
```

You could also specify start_date and end_date like the follows
``` python
config = "roi_url=inputs/S2_BC_ALB_fireCenter.geojson satellite=sentinel2 start_date=2021-08-01 end_date=2021-08-02"
```

You could also create your own ROI in geojson in https://geojson.io/, save it into inputs folder.

## check updated data in the wildfire monitor app:
https://eo4wildfire.users.earthengine.app/view/wildfire-monitor-us


## Other (no need to follow)
export env (for export only)
``` bash
conda env export -f environment.yml
```

``` bash
conda env export -f env.yml --no-builds
```

create python environment from yml
``` bash
conda env create -f env1.yml
```

config python environment from yml
``` bash
conda env update --file env.yml --prune
```