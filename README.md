# Plt Anomaly Detection Tool
### PLT-BRIL, CMS, CERN
---
### Description

This repo is a efficient implementation of an anomaly detection algorithm suited for the data coming from the PLT-BRIL detector, is is intended to be robust to experimental noise and not highly tuneable.

For now, the implementation is a Proof-of-Concept, and looks forward to be generalized to other usecases and dockerized.

---

### Quick start

From a lxplus instance you can run the following command:

```bash
source setup.sh
```
This will setup the environment and load the python modules. In addition it will help you generate the mount to the BRILDATA.

Otherwise, you can follow the examples in .ipynb

---

### Contributing

All the dependencies are managed via pipenv for reproducibility and ease of use. We lint all the code with flake8 and black and shall use precode to enforce the coding style.

Please add changes to a new branch, and considering test passing, the PR to the master branch.

--- 

**Contact**

Contact @munozariasjm for any issues or questions related to the code.
