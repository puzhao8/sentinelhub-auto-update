"# sentinelhub-auto-query" 

# Config Environment
## 1. Install anaconda
https://docs.anaconda.com/anaconda/install/index.html
``` bash
conda env create -f env1.yml
```

## 2. Install ESA SNAP Desktop Software 
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
``` bash
python wandb_main_run_multi_scripts.py 
```

This command line will run sentinel_query_download.py and update_sentinel_for_gee.py at the same time, and you can change the variable config in wandb_main_run_multi_scripts.py:

For Sentinel-1, the default start_date is the day before today, and end_date is the day after today.
``` python
config = "roi_url=inputs/S1_split_US.geojson satellite=sentinel1"
```
For Sentinel-2, you can change it into 
``` python
config = "roi_url=inputs/S2_BC_ALB_fireCenter.geojson satellite=sentinel2"
```

You could also specify start_date and end_date like the follows
``` python
config = "roi_url=inputs/S2_BC_ALB_fireCenter.geojson satellite=sentinel2 start_date=2021-08-01 end_date=2021-08-02"
```

You could also create your own ROI in geojson in https://geojson.io/, save it into inputs folder.



## Other (no need to follow)
### export env (for export only)
```
conda env export -f env.yml --no-builds
```

### config python environment from yml
```
conda env update --file env.yml --prune
```