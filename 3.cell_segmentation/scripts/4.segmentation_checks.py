#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pathlib

import pandas as pd
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
masks = ["organoid_masks", "nuclei_masks", "cell_masks"]


# In[4]:


expected_count = 0
missing_count = 0
missing_list = []
for patient in tqdm.tqdm(patient_ids, desc="Patients"):
    for illum_corr_sub_path in illumcorr_paths:
        illum_corr_path = pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/{illum_corr_sub_path}/"
        )
        well_fovs = [wf.stem for wf in illum_corr_path.glob("*")]
        for well_fov in well_fovs:
            for mask in masks:
                mask_path = pathlib.Path(
                    f"{image_base_dir}/data/{patient}/2D_analysis/{illum_corr_sub_path}/{well_fov}/{well_fov}_{mask}.tiff"
                ).resolve()
                expected_count += 1
                if not mask_path.exists():
                    missing_list.append(mask_path)
                    missing_count += 1


# In[5]:


print(f"Total number of expected masks: {expected_count:,}")
print(f"Total number of masks found: {(expected_count - missing_count):,}")
print(f"Total number of missing masks: {missing_count:,}")


# In[6]:


missing_list = [str(x.parent) for x in missing_list]
missing_list = list(set(missing_list))
df = pd.DataFrame(missing_list, columns=["Missing Masks"])


# In[7]:


df["patient"] = df["Missing Masks"].apply(lambda x: x.split("/")[-4])
df["well_fov"] = df["Missing Masks"].apply(lambda x: x.split("/")[-1])
df.drop(columns=["Missing Masks"], inplace=True)
df.drop_duplicates(inplace=True)
df.sort_values(by=["patient", "well_fov"], inplace=True)
df.head()


# In[8]:


# write to the loadfile
loadfile_path = pathlib.Path("../loadfiles/segmentation_loadfile.txt").resolve()
loadfile_path.parent.mkdir(parents=True, exist_ok=True)
with open(loadfile_path, "w") as f:
    for idx, row in df.iterrows():
        f.write(f"{row['patient']}\t{row['well_fov']}\n")
