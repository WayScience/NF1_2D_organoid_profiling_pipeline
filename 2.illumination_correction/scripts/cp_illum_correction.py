#!/usr/bin/env python
# coding: utf-8

# # Perform illumination correction and save the images

# ## Import libraries

# In[1]:


import os
import pathlib
import pprint

from arg_parsing_utils import check_for_missing_args, parse_args
from notebook_init_utils import bandicoot_check, init_notebook

import cp_parallel
from cp_parallel import run_cellprofiler_parallel

root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)


# In[2]:


if not in_notebook:
    args_dict = parse_args()
    patient = args_dict["patient"]
    check_for_missing_args(
        patient=patient,
    )
else:
    patient = "NF0018_T6"


# ## Set paths and variables

# In[3]:


# set the run type for the parallelization
run_name = "illum_correction"

# set path for CellProfiler pipeline
path_to_pipeline = pathlib.Path("../pipelines/illum.cppipe").resolve(strict=True)


# directory where max-projected images are within the folder
images_dir = pathlib.Path(
    f"{image_base_dir}/data/{patient}/2D_analysis/0a.zmax_proj/"
).resolve(strict=True)

# Get the plate name from the folder name
plate_name = images_dir.stem  # Get the folder name as the plate name
print(plate_name)


# In[4]:


# get the number of images in the directory
well_fovs = list(images_dir.glob("*"))
well_fovs = [x for x in well_fovs if x.is_dir()]
well_fovs = [x.stem for x in well_fovs]


# ## Create dictionary to process data

# In[5]:


plate_info_dictionary = {}
for well_fov in well_fovs:
    # set the output directory for the well
    plate_info_dictionary[f"zmax_proj_{well_fov}"] = {
        "path_to_images": pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/0a.zmax_proj/{well_fov}"
        ).resolve(),
        "path_to_output": pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/1a.zmax_proj_illum_correction/{well_fov}"
        ).resolve(),
        "path_to_pipeline": path_to_pipeline,
    }
    plate_info_dictionary[f"middle_slice_{well_fov}"] = {
        "path_to_images": pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/0b.middle_slice/{well_fov}"
        ).resolve(),
        "path_to_output": pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/1b.middle_slice_illum_correction/{well_fov}"
        ).resolve(),
        "path_to_pipeline": path_to_pipeline,
    }
    plate_info_dictionary[f"middle_n_slice_max_proj_{well_fov}"] = {
        "path_to_images": pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/0c.middle_n_slice_max_proj/{well_fov}"
        ).resolve(),
        "path_to_output": pathlib.Path(
            f"{image_base_dir}/data/{patient}/2D_analysis/1c.middle_n_slice_max_proj_illum_correction/{well_fov}"
        ).resolve(),
        "path_to_pipeline": path_to_pipeline,
    }


# In[6]:


# only run well_fovs if < 4 files in the output directory
filtered_plate_info_dictionary = {}
missing_list = []
for well_fov_key in plate_info_dictionary:
    output_dir = plate_info_dictionary[well_fov_key]["path_to_output"]
    num_files = len(list(output_dir.glob("*.tiff")))
    if num_files < 4:
        filtered_plate_info_dictionary[well_fov_key] = plate_info_dictionary[
            well_fov_key
        ]
        missing_list.append(output_dir)
well_fovs = list(filtered_plate_info_dictionary.keys())
well_fovs = [x.split("_")[-1] for x in well_fovs]
pprint.pprint(filtered_plate_info_dictionary)


# In[7]:


print(f"""Now runnning illumination correction for
        patient: {patient}
        and {len(well_fovs)} wells
        for both zmax_proj and middle_slice
        bringing us to a total of {len(filtered_plate_info_dictionary)} runs""")


# In[8]:


# delete the output directories for CP rerun if they exist
for key in filtered_plate_info_dictionary:
    output_dir = filtered_plate_info_dictionary[key]["path_to_output"]
    if output_dir.exists():
        print(f"Deleting existing output directory: {output_dir}")
        for file in output_dir.glob("*"):
            file.unlink()
        output_dir.rmdir()


# ## Perform illumination correction on data
#
# The function being called is called "run_cellprofiler_parallel" but can be used if there is only one plate to run. We can also split the data by well and process that way in parallel, but we choose to process at all at once for now.
#
# Note: This code cell was not ran as we prefer to perform CellProfiler processing tasks via `sh` file (bash script) which is more stable.

# In[9]:


if len(filtered_plate_info_dictionary) == 0:
    print("All illumination correction outputs already exist. Exiting.")
else:
    cp_parallel.run_cellprofiler_parallel(
        plate_info_dictionary=filtered_plate_info_dictionary, run_name=run_name
    )
