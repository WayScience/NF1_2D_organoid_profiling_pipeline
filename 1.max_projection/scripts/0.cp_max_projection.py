#!/usr/bin/env python
# coding: utf-8

# # Perform maximum projection and save the images

# ## Import libraries

# In[1]:


import pathlib

import tifffile
import tqdm

# In[2]:


# input images directory
images_dir = pathlib.Path("../../data/NF0014/zstack_images/").resolve(strict=True)
# output images directory
output_dir = pathlib.Path("../../data/NF0014/zmax_proj/").resolve()


# In[3]:


# get a list of all of the tiff files in the directory
tiff_files = list(images_dir.rglob("*.tif"))
tiff_files.sort()
for tiff_file in tqdm.tqdm(tiff_files):
    # load the first tiff file to get the metadata
    image = tifffile.TiffFile(tiff_file)
    # z max projection
    max_proj = image.asarray().max(axis=0)
    # save the middle slice as a new tiff file
    output_file_dir = output_dir / str(tiff_file.parent).split("/")[-1] / tiff_file.name
    output_file_dir.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(output_file_dir, max_proj)
