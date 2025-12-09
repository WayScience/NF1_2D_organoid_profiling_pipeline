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


if not in_notebook:
    args_dict = parse_args()
    patient = args_dict["patient"]
    check_for_missing_args(
        patient=patient,
    )
else:
    patient = "NF0014_T1"


# In[3]:


# input images directory
images_dir = pathlib.Path(f"{image_base_dir}/data/{patient}/zstack_images/").resolve(
    strict=True
)
# output images directory
output_dir = pathlib.Path(
    f"{image_base_dir}/data/{patient}/2D_analysis/0c.middle_n_slice_max_proj/"
).resolve()
output_dir.mkdir(parents=True, exist_ok=True)


# In[4]:


# set n
n = 3


# In[5]:


# get a list of all of the tiff files in the directory
tiff_files = list(images_dir.rglob("*.tif"))
tiff_files.sort()
for tiff_file in tqdm.tqdm(tiff_files):
    try:
        output_file_dir = (
            output_dir / str(tiff_file.parent).split("/")[-1] / tiff_file.name
        )
        output_file_dir.parent.mkdir(parents=True, exist_ok=True)
        if output_file_dir.exists():
            continue
        # load the first tiff file to get the metadata
        image = tifffile.TiffFile(tiff_file)
        number_of_slices = image.series[0].shape[0]
        # get the middle most slice
        middle_slice_index = number_of_slices // 2
        # get the middle n slices
        start_index = max(0, middle_slice_index - n // 2)
        end_index = min(number_of_slices, middle_slice_index + n // 2 + 1)
        middle_n_slices = image.series[0].asarray()[start_index:end_index, :, :]
        # get the max projection of the middle n slices
        middle_slice_max_proj = middle_n_slices.max(axis=0)
        # save the middle slice max projection as a new tiff file
        tifffile.imwrite(output_file_dir, middle_slice_max_proj)
    except Exception as e:
        print(f"Error processing file {tiff_file}: {e}")
