#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib
import pprint
import sys

import pandas as pd

# Get the current working directory
cwd = pathlib.Path.cwd()

if (cwd / ".git").is_dir():
    root_dir = cwd

else:
    root_dir = None
    for parent in cwd.parents:
        if (parent / ".git").is_dir():
            root_dir = parent
            break

# Check if a Git root directory was found
if root_dir is None:
    raise FileNotFoundError("No Git root directory found.")

sys.path.append(f"{root_dir}/utils/")
# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False


# In[2]:


patients_dir = pathlib.Path(f"{root_dir}/data/").resolve(
    strict=True
)  # directory containing patient folders
# get a list of patient directories
patient_dirs = [d for d in patients_dir.iterdir() if d.is_dir()]
patient_dirs
# get a list of the well_fov directories for each patient
well_fov_dirs = [
    x
    for patient in patient_dirs
    for x in pathlib.Path(f"{patient}/middle_slice_illum_correction").iterdir()
    if x.is_dir()
]
well_fov_dirs.sort()
well_fov_df = pd.DataFrame(well_fov_dirs, columns=["dir_path"])
well_fov_df["patient"] = well_fov_df["dir_path"].apply(
    lambda x: str(x.parent).split("/")[-2]
)
well_fov_df["well_fov"] = well_fov_df["dir_path"].apply(lambda x: x.stem)
well_fov_df


# In[3]:


present_files = 0
missing_files = 0
missing_files_list = []
for index, row in well_fov_df.iterrows():
    patient = row["patient"]
    well_fov = row["well_fov"]
    middle_slice_dir_to_check = pathlib.Path(
        f"{root_dir}/data/{patient}/cellprofiler_middle_slice_output/{well_fov}/"
    ).resolve()
    max_z_slice_dir_to_check = pathlib.Path(
        f"{root_dir}/data/{patient}/cellprofiler_zmax_proj_output/{well_fov}/"
    ).resolve()
    if not middle_slice_dir_to_check.is_dir():
        missing_files += 1
        missing_files_list.append(str(middle_slice_dir_to_check))
    else:
        present_files += 1
    if not max_z_slice_dir_to_check.is_dir():
        missing_files += 1
        missing_files_list.append(str(max_z_slice_dir_to_check))
    else:
        present_files += 1

print(f"Total directories checked: {len(well_fov_df) * 2}")
print(f"Present directories: {present_files}")
print(f"Missing directories: {missing_files}")
print("Missing directories list:")
pprint.pprint(missing_files_list)
