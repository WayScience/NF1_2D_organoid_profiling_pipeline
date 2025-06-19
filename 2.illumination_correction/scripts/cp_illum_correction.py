#!/usr/bin/env python
# coding: utf-8

# # Perform illumination correction and save the images

# ## Import libraries

# In[ ]:


import argparse
import pathlib
import sys

sys.path.append("../../utils")
import cp_parallel

# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False

print(in_notebook)


# In[ ]:


if not in_notebook:
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--patient",
        type=str,
        help="Patient ID to use for the segmentation",
    )

    args = parser.parse_args()
    patient = args.patient

else:
    patient = "NF0014"


# ## Set paths and variables

# In[3]:


# set the run type for the parallelization
run_name = "illum_correction"

# set path for CellProfiler pipeline
path_to_pipeline = pathlib.Path("../pipelines/illum.cppipe").resolve(strict=True)


# directory where max-projected images are within the folder
images_dir = pathlib.Path(f"../../data/{patient}/zmax_proj/").resolve(strict=True)

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
            f"../../data/{patient}/zmax_proj/{well_fov}"
        ).resolve(),
        "path_to_output": pathlib.Path(
            f"../../data/{patient}/zmax_proj_illum_correction/{well_fov}"
        ).resolve(),
        "path_to_pipeline": path_to_pipeline,
    }
    plate_info_dictionary[f"middle_slice{well_fov}"] = {
        "path_to_images": pathlib.Path(
            f"../../data/{patient}/middle_slice/{well_fov}"
        ).resolve(),
        "path_to_output": pathlib.Path(
            f"../../data/{patient}/middle_slice_illum_correction/{well_fov}"
        ).resolve(),
        "path_to_pipeline": path_to_pipeline,
    }


# ## Perform illumination correction on data
#
# The function being called is called "run_cellprofiler_parallel" but can be used if there is only one plate to run. We can also split the data by well and process that way in parallel, but we choose to process at all at once for now.
#
# Note: This code cell was not ran as we prefer to perform CellProfiler processing tasks via `sh` file (bash script) which is more stable.

# In[6]:


cp_parallel.run_cellprofiler_parallel(
    plate_info_dictionary=plate_info_dictionary, run_name=run_name
)
