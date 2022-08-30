# Plt Anomaly Detection Tool
### PLT-BRIL, CMS, CERN
---
### Description

This repo is a efficient implementation of an anomaly detection algorithm suited for the data coming from the PLT-BRIL detector, is is intended to be robust to experimental noise and not highly tuneable.

For now, the implementation is a Proof-of-Concept, and looks forward to be generalized to other usecases and dockerized.

---

### Quick start

We recommend to use all the commands within a lxplus instance. To beguin, please be in the directory of this repository.

```bash
cd AnomalyDetection
```

From here, we should create a new pipenv environment to install the required packages. This can be easily done via the script we prepared:

```bash
source setup.sh
```
Now, we prepared a module to easily mount the data from the PLT-BRIL detector. To do so, we need to run the following command in a python shell:

```python
from src.data.mounting_tool import MountData
mounter = MountData(user="YOUR_CMSUSR", password="YOUR_password")
mounter.create_mount(mount_source="brildev1:/brildata/22/", mount_target="./Files/22")
```
This will mount all the files containing fills in 2022 in the directory `./Files/22`. And the data will be unmounted when the lxplus instance is closed.


---

### Contributing

All the dependencies are managed via pipenv for reproducibility and ease of use. We lint all the code with flake8 and black and shall use precode to enforce the coding style.

Please add changes to a new branch, and considering test passing, the PR to the master branch.

--- 

**Contact**

Contact @munozariasjm for any issues or questions related to the code.
