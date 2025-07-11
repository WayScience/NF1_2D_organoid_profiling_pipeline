#!/usr/bin/env python
# coding: utf-8

# # Perform analysis (segmentation and feature extraction) and save features as an SQLite database

# ## Import libraries

# In[1]:


import argparse
import pathlib
import pprint
import sys

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
import cp_parallel

# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False


# In[2]:


if not in_notebook:
    print("Running as script")
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--patient",
        type=str,
        help="Patient ID",
    )

    parser.add_argument(
        "--well_fov",
        type=str,
        help="Path to the input directory containing the tiff images",
    )

    args = parser.parse_args()
    well_fov = args.well_fov
    patient = args.patient
else:
    print("Running in a notebook")
    well_fov = "C2-1"
    patient = "NF0014"

middle_slice_input = pathlib.Path(
    f"{root_dir}/data/{patient}/middle_slice_illum_correction/{well_fov}"
).resolve(strict=True)
max_projected_input = pathlib.Path(
    f"{root_dir}/data/{patient}/zmax_proj_illum_correction/{well_fov}"
).resolve(strict=True)


# ## Set paths and variables

# In[3]:


# set the run type for the parallelization
run_name = f"{patient}_{well_fov}"

# set path for CellProfiler pipeline
path_to_pipeline = pathlib.Path(
    f"{root_dir}/3.feature_extraction/pipelines/analysis.cppipe"
).resolve(strict=True)

# Get the plate name from the folder name
plate_name = f"{patient}_{well_fov}"  # Get the folder name as the plate name


# ## Create dictionary to process data

# In[4]:


plate_info_dictionary = {}
# create plate info dictionary with all parts of the CellProfiler CLI command to run in parallel
for images_dir in [middle_slice_input, max_projected_input]:
    plate_info_dictionary[f"{plate_name}_{str(images_dir.parent.name)}"] = {
        "path_to_images": images_dir,
        "path_to_output": pathlib.Path(
            f"{root_dir}/data/{patient}/cellprofiler_{str(images_dir.parent.name.split('_illum_correction')[0])}_output/{well_fov}/"
        ).resolve(),
        "path_to_pipeline": path_to_pipeline,
    }

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Perform CellProfiler analysis on data
#
# The function being called is called "run_cellprofiler_parallel" but can be used if there is only one plate to run. We can also split the data by well and process that way in parallel, but we choose to process at all at once for now.
#
# Note: This code cell was not ran as we prefer to perform CellProfiler processing tasks via `sh` file (bash script) which is more stable.

# In[5]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=plate_info_dictionary, run_name=run_name
)
