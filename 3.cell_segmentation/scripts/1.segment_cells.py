#!/usr/bin/env python
# coding: utf-8

# This notebook focuses on trying to find a way to segment cells within organoids properly.
# The end goal is to segment cells and extract morphology features from CellProfiler.
# These masks must be imported into CellProfiler to extract features.

# ## import libraries

# In[1]:


import os
import pathlib

import matplotlib.pyplot as plt

# Import dependencies
import numpy as np
import skimage
import tifffile
from arg_parsing_utils import check_for_missing_args, parse_args
from notebook_init_utils import bandicoot_check, init_notebook
from skimage import io, segmentation

root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)


# ## parse args and set paths

# If a notebook run the hardcoded paths.
# However, if this is run as a script, the paths are set by the parsed arguments.

# In[2]:


if not in_notebook:
    args_dict = parse_args()
    patient = args_dict["patient"]
    well_fov = args_dict["well_fov"]
    clip_limit = args_dict["clip_limit"]
    twoD_method = args_dict["twoD_method"]
    overwrite = args_dict.get("overwrite", False)
    check_for_missing_args(
        patient=patient,
        well_fov=well_fov,
        clip_limit=clip_limit,
        twoD_method=twoD_method,
    )
else:
    print("Running in a notebook")
    patient = "NF0040_T1"
    well_fov = "E7-1"
    clip_limit = 0.01
    twoD_method = "middle_n"
    overwrite = True


if twoD_method == "middle":
    input_dir = pathlib.Path(
        f"{image_base_dir}/data/{patient}/2D_analysis/1b.middle_slice_illum_correction/{well_fov}"
    ).resolve(strict=True)

elif twoD_method == "zmax":
    input_dir = pathlib.Path(
        f"{image_base_dir}/data/{patient}/2D_analysis/1a.zmax_proj_illum_correction/{well_fov}"
    ).resolve(strict=True)
elif twoD_method == "middle_n":
    input_dir = pathlib.Path(
        f"{image_base_dir}/data/{patient}/2D_analysis/1c.middle_n_slice_max_proj_illum_correction/{well_fov}"
    ).resolve(strict=True)
else:
    raise ValueError(f"Unknown twoD_method: {twoD_method}")


labels_path = input_dir / f"{well_fov}_cell_masks.tiff"

mask_path = input_dir


# ## Set up images, paths and functions

# In[3]:


if overwrite or not labels_path.exists():
    image_extensions = {".tif", ".tiff"}
    files = sorted(input_dir.glob("*"))
    files = [str(x) for x in files if x.suffix in image_extensions]
    # get the nuclei image
    for f in files:
        if "555" in f:
            cell = io.imread(f)
        elif "nuclei_mask" in f:
            nuclei_mask = io.imread(f)
    cell = np.array(cell)
    cell = skimage.exposure.equalize_adapthist(cell, clip_limit=clip_limit)
    nuclei_mask = np.array(nuclei_mask)
    if in_notebook:
        plt.imshow(cell, cmap="gray")
        plt.axis("off")
        plt.show()
        labels = np.zeros_like(cell, dtype=np.int32)
    # get the seeds from the nuclei mask
    seeds = skimage.measure.label(nuclei_mask, connectivity=2)
    labels = segmentation.watershed(cell, markers=seeds)
    # make sure the background is labeled as 0
    labels[labels == -1] = 0
    # set the largest label to 0 (background)
    largest_label = np.bincount(labels.ravel()).argmax()
    labels[labels == largest_label] = 0
    # # save the labels
    tifffile.imwrite(labels_path, labels.astype(np.uint16))


# ## Watershed the cells from the nuclei

# In[4]:


if in_notebook:
    plot = plt.figure(figsize=(10, 5))
    plt.figure(figsize=(10, 10))
    plt.subplot(131)
    plt.imshow(labels, cmap="nipy_spectral")
    plt.title("mask")
    plt.axis("off")
    plt.subplot(132)
    plt.imshow(nuclei_mask, cmap="nipy_spectral")
    plt.title("nuclei mask")
    plt.axis("off")

    plt.subplot(133)
    plt.imshow(cell, cmap="gray")
    plt.title("raw")
    plt.axis("off")
