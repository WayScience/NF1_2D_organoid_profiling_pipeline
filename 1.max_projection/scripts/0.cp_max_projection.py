#!/usr/bin/env python
# coding: utf-8

# # Perform maximum projection and save the images

# ## Import libraries

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


if not in_notebook:
    args_dict = parse_args()
    patient = args_dict["patient"]
    check_for_missing_args(
        patient=patient,
    )
else:
    patient = "NF0016_T1"


# In[3]:


# input images directory
images_dir = pathlib.Path(f"{image_base_dir}/data/{patient}/zstack_images/").resolve(
    strict=True
)
# output images directory
output_dir = pathlib.Path(
    f"{image_base_dir}/data/{patient}/2D_analysis/0a.zmax_proj/"
).resolve()
output_dir.mkdir(parents=True, exist_ok=True)


# In[4]:


# get a list of all of the tiff files in the directory
tiff_files = list(images_dir.rglob("*.tif"))
tiff_files.sort()
for tiff_file in tqdm.tqdm(tiff_files):
    output_file_dir = output_dir / str(tiff_file.parent).split("/")[-1] / tiff_file.name
    output_file_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_file_dir.exists():
        continue
    # load the first tiff file to get the metadata
    image = tifffile.TiffFile(tiff_file)
    # z max projection
    max_proj = image.asarray().max(axis=0)
    # save the middle slice as a new tiff file

    tifffile.imwrite(output_file_dir, max_proj)
