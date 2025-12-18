#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pathlib

import tifffile
import tqdm
from arg_parsing_utils import check_for_missing_args, parse_args
from notebook_init_utils import bandicoot_check, init_notebook

root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)


# In[2]:


patient_ids_path = pathlib.Path(f"{root_dir}/data/patient_IDs.txt").resolve(strict=True)
patient_ids = patient_ids_path.read_text().splitlines()
patient_ids


# In[3]:


illumcorr_paths = [
    "1a.zmax_proj_illum_correction",
    "1b.middle_slice_illum_correction",
    "1c.middle_n_slice_max_proj_illum_correction",
]
channels = ["405", "488", "555", "640"]


# In[4]:


expected_count = 0
missing_count = 0
missing_list = []
for patient in tqdm.tqdm(patient_ids, desc="Patients"):
    # get the number of well_fovs present from the zstack_images dir
    well_fovs = pathlib.Path(f"{image_base_dir}/data/{patient}/zstack_images").glob("*")
    well_fovs = [wf.stem for wf in well_fovs]
    for well_fov in well_fovs:
        for channel in channels:
            for illum_corr_sub_path in illumcorr_paths:
                expected_count += 1
                illum_corr_path = pathlib.Path(
                    f"{image_base_dir}/data/{patient}/2D_analysis/{illum_corr_sub_path}/{well_fov}/{well_fov}_{channel}_illumcorrect.tiff"
                )
                if not illum_corr_path.exists():
                    missing_count += 1
                    missing_list.append(illum_corr_path)
print(f"Expected illumination corrected images: {expected_count}")
print(f"Missing illumination corrected images: {missing_count}")


# In[5]:


missing_list = [str(x.parent) for x in missing_list]
missing_list = list(set(missing_list))
print("Missing illumination corrected image directories:")
for missing in missing_list:
    print(missing)
