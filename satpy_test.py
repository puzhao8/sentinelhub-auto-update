
# %%
from stat import FILE_ATTRIBUTE_NO_SCRUB_DATA
from satpy.scene import Scene
from satpy import find_files_and_readers
from datetime import datetime


# %%
from pathlib import Path
datafolder = Path("G:\PyProjects\sentinelhub-auto-update\outputs")
url_MOD02HKM = datafolder / "MOD02HKM.A2022246.1015.061.2022246111842.NRT.hdf"
url_MOD021KM = datafolder / "MOD021KM.A2022247.0025.061.2022247013902.NRT.hdf"
url_MOD02QKM = datafolder / "MOD02QKM.A2022248.1000.061.2022248110709.NRT.hdf"

scn = Scene(filenames=[str(url_MOD021KM)])