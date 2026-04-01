#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import pathlib

import numpy as np
import pandas as pd
import tifffile
from image_analysis_2D.file_utils.arg_parsing_utils import (
    check_for_missing_args,
    parse_args,
)
from image_analysis_2D.file_utils.notebook_init_utils import (
    bandicoot_check,
    init_notebook,
)

root_dir, in_notebook = init_notebook()
if in_notebook:
    import tqdm.notebook as tqdm
else:
    import tqdm
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)


# In[4]:


patient_ids_path = pathlib.Path(f"{root_dir}/data/patient_IDs.txt").resolve(strict=True)
patient_ids = patient_ids_path.read_text().splitlines()
validated_mask_images_path = pathlib.Path(
    "../results/validated_mask_images.parquet"
).resolve()
validated_mask_images_path.parent.mkdir(parents=True, exist_ok=True)
if validated_mask_images_path.exists():
    validated_masks_list = pd.read_parquet(validated_mask_images_path)[
        "validated_masks"
    ].tolist()
else:
    validated_masks_list = []


# In[5]:


illumcorr_paths = [
    "0a.zmax_proj",
    "0b.middle_slice",
    "0c.middle_n_slice_max_proj",
]
masks = ["organoid_mask", "nuclei_mask", "cell_mask"]


# In[6]:


expected_count = 0
present_count = 0
empty_count = 0
empty_masks = []
for patient in tqdm.tqdm(patient_ids, desc="Patients", leave=True, unit="patient"):
    for illum_corr_sub_path in illumcorr_paths:
        illum_corr_path = pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/{illum_corr_sub_path}/"
        )
        well_fovs = [wf.stem for wf in illum_corr_path.glob("*")]
        for well_fov in tqdm.tqdm(
            well_fovs,
            desc=f"Processing well FOVs for patient {patient}",
            leave=False,
            unit="well FOV",
        ):
            for mask in masks:
                mask_path = pathlib.Path(
                    f"{image_base_dir}/data/{patient}/2D_analysis/{illum_corr_sub_path}/{well_fov}/{well_fov}_{mask}.tiff"
                ).resolve()
                expected_count += 1
                if mask_path.exists() and str(mask_path) not in validated_masks_list:
                    mask_image = tifffile.imread(mask_path)
                    if np.unique(mask_image).size > 1:
                        validated_masks_list.append(str(mask_path))
                    else:
                        empty_count += 1
                        empty_masks.append(str(mask_path))
                else:
                    present_count += 1
print(
    f"Validated {len(validated_masks_list)} masks out of {expected_count} expected masks, with {empty_count} empty masks."
)
print(f"{present_count / expected_count:.2%} of expected masks were validated.")


# In[7]:


df = pd.DataFrame({"validated_masks": validated_masks_list})
df = df.astype(str)
df.to_parquet(validated_mask_images_path, index=False)
print(f"Total validated masks: {len(validated_masks_list)}")


# In[8]:


if len(empty_masks) > 0:
    print(f"There are {len(empty_masks)} empty masks found.")
else:
    print("No empty masks found.")
