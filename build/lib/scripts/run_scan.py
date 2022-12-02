# %%
import sys

sys.path.append("..")
import warnings
import json

warnings.filterwarnings("ignore")

# %%
from src.model.searcher import AnomalySearcher
from src.data.mounting_tool import MountData

# %% [markdown]
# ### Importing and cleaning the data
#
# In setmount we have a little script to create the mount to the dessired data.
# Modify the bash script to make it work for your computing account and cmsusr
#

# %%
MOUNT_TARGET = "/afs/cern.ch/user/j/jmunozar/private/InProcess/plt/mounts/h5s/"

# %%
with open("../secrets.json", "r") as f:
    config = json.load(f)
mounter = MountData(user="jmunozar", password=config["pass"])
mounter.create_mount(mount_source="brildev1:/brildata/22/", mount_target=MOUNT_TARGET)

# %% [markdown]
# %%
if __name__ == "__main__":
    AnomalySearcher().run_scan(
        mount_path=MOUNT_TARGET,
        output_path=f"/afs/cern.ch/user/j/jmunozar/private/InProcess/plots_all_fill_reports",
        make_anomalous_plots=True,
        overwrite=True,
        progress_bar=True,
        make_normal_plots=True,
    )

# %%
