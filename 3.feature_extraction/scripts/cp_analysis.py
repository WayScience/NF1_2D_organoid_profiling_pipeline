#!/usr/bin/env python
# coding: utf-8

# # Perform analysis (segmentation and feature extraction) and save features as an SQLite database

# ## Import libraries

# In[1]:


import os
import pathlib
import pprint
import time

import psutil
from arg_parsing_utils import check_for_missing_args, parse_args
from notebook_init_utils import bandicoot_check, init_notebook

import cp_parallel
from cp_parallel import run_cellprofiler_parallel

root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)


# In[2]:


# begin profiling of time, and memory
start_time = time.time()
start_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # in MB


# In[3]:


if not in_notebook:
    args_dict = parse_args()
    patient = args_dict["patient"]
    well_fov = args_dict["well_fov"]
    check_for_missing_args(
        patient=patient,
        well_fov=well_fov,
    )
else:
    print("Running in a notebook")
    well_fov = "C2-1"
    patient = "NF0014_T1"


max_projected_input = pathlib.Path(
    f"{image_base_dir}/data/{patient}/2D_analysis/1a.zmax_proj_illum_correction/{well_fov}"
).resolve(strict=True)
middle_slice_input = pathlib.Path(
    f"{image_base_dir}/data/{patient}/2D_analysis/1b.middle_slice_illum_correction/{well_fov}"
).resolve(strict=True)
middle_n_input = pathlib.Path(
    f"{image_base_dir}/data/{patient}/2D_analysis/1c.middle_n_slice_max_proj_illum_correction/{well_fov}"
).resolve(strict=True)


# ## Set paths and variables

# In[4]:


# set the run type for the parallelization
run_name = f"{patient}_{well_fov}"

# set path for CellProfiler pipeline
path_to_pipeline_sc = pathlib.Path(
    f"{root_dir}/3.feature_extraction/pipelines/analysis_single_cell.cppipe"
).resolve(strict=True)
path_to_pipeline_organoid = pathlib.Path(
    f"{root_dir}/3.feature_extraction/pipelines/analysis_organoid.cppipe"
).resolve(strict=True)
# Get the plate name from the folder name
plate_name = f"{patient}_{well_fov}"  # Get the folder name as the plate name


# ## Create dictionary to process data

# In[5]:


plate_info_dictionary = {}
# create plate info dictionary with all parts of the CellProfiler CLI command to run in parallel
for images_dir in [middle_slice_input, max_projected_input, middle_n_input]:
    if "zmax_proj" in str(images_dir):
        output_path = f"{root_dir}/data/{patient}/2D_analysis/2a.cellprofiler_{str(images_dir.parent.name.split('_illum_correction')[0].split('1a.')[1])}_output/{well_fov}/"
    elif "middle_slice" in str(images_dir):
        output_path = f"{root_dir}/data/{patient}/2D_analysis/2b.cellprofiler_{str(images_dir.parent.name.split('_illum_correction')[0].split('1b.')[1])}_output/{well_fov}/"
    elif "middle_n" in str(images_dir):
        output_path = f"{root_dir}/data/{patient}/2D_analysis/2c.cellprofiler_{str(images_dir.parent.name.split('_illum_correction')[0].split('1c.')[1])}_output/{well_fov}/"
    for object_type in ["single_cell", "organoid"]:
        pipeline = (
            path_to_pipeline_sc
            if object_type == "single_cell"
            else path_to_pipeline_organoid
        )

        plate_info_dictionary[
            f"{plate_name}_{str(images_dir.parent.name)}_{object_type}"
        ] = {
            "path_to_images": images_dir,
            "path_to_output": pathlib.Path(output_path).resolve(),
            "path_to_pipeline": pipeline,
        }

# view the dictionary to assess that all info is added correctly
if in_notebook:
    pprint.pprint(plate_info_dictionary, indent=4)


# In[ ]:


# check if there is a sqlite db already present, if so remove the run from the dictionary
plates_to_run = {}
for plate_name, plate_info in plate_info_dictionary.items():
    if not plate_info["path_to_output"].exists():
        plate_info["path_to_output"].mkdir(parents=True, exist_ok=True)
    sqlite_files = list(plate_info["path_to_output"].glob("*.sqlite"))
    if len(sqlite_files) == 0:
        plates_to_run[plate_name] = plate_info
    else:
        print(
            f"SQLite database already present for {plate_name}, skipping CellProfiler run."
        )
if in_notebook:
    pprint.pprint(plates_to_run, indent=4)


# ## Perform CellProfiler analysis on data
#
# The function being called is called "run_cellprofiler_parallel" but can be used if there is only one plate to run. We can also split the data by well and process that way in parallel, but we choose to process at all at once for now.
#
# Note: This code cell was not ran as we prefer to perform CellProfiler processing tasks via `sh` file (bash script) which is more stable.

# In[7]:


if len(plates_to_run) == 0:
    print("All runs have already ran")
else:
    cp_parallel.run_cellprofiler_parallel(
        plate_info_dictionary=plate_info_dictionary, run_name=run_name
    )


# In[8]:


end_time = time.time()
end_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # in MB
time_elapsed = end_time - start_time
memory_used = end_memory - start_memory
print(f"Time elapsed: {time_elapsed:.2f} seconds")
print(f"Time elapsed: {time_elapsed / 60:.2f} minutes")
print(f"Time elapsed: {time_elapsed / 3600:.2f} hours")
print(f"Memory used: {memory_used:.2f} MB")
print(f"Memory used: {memory_used / 1024:.2f} GB")
