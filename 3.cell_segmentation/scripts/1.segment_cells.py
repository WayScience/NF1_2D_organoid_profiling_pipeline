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
    patient = "NF0014_T1"
    well_fov = "C4-1"
    clip_limit = 0.01
    twoD_method = "zmax"
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
            nuclei_mask_path = f
            nuclei_mask = io.imread(f)
    cell = np.array(cell)
    cell = skimage.exposure.equalize_adapthist(cell, clip_limit=clip_limit)
    # nuclei_mask = np.array(nuclei_mask)

    # get the seeds from the nuclei mask
    # seeds = skimage.measure.label(nuclei_mask, connectivity=1)
    cell = skimage.filters.sobel(cell, mask=cell > 0)
    labels = segmentation.watershed(cell, markers=nuclei_mask)
    # make sure the background is labeled as 0
    # set the largest label to 0 (background)
    largest_label = np.bincount(labels.ravel()).argmax()
    labels[labels == largest_label] = 0

    # remove nuclei masks that do not have any cell pixels
    unique_nuclei = np.unique(nuclei_mask)
    for nucleus_label in unique_nuclei:
        if nucleus_label == 0:
            continue
        # get the mask for the nucleus
        nucleus_mask = nuclei_mask == nucleus_label
        # check if there are any cell pixels in this nucleus
        overlapping_cell_labels = np.unique(labels[nucleus_mask])
        overlapping_cell_labels = overlapping_cell_labels[
            overlapping_cell_labels != 0
        ]  # exclude background
        if len(overlapping_cell_labels) == 0:
            # remove this nucleus by setting its label to 0
            nuclei_mask[nucleus_mask] = 0

    # remove the cell labels that do not have any nuclei pixels
    unique_cells = np.unique(labels)
    for cell_label in unique_cells:
        if cell_label == 0:
            continue
        # get the mask for the cell
        cell_mask = labels == cell_label
        # check if there are any nuclei pixels in this cell
        overlapping_nuclei_labels = np.unique(nuclei_mask[cell_mask])
        overlapping_nuclei_labels = overlapping_nuclei_labels[
            overlapping_nuclei_labels != 0
        ]  # exclude background
        if len(overlapping_nuclei_labels) == 0:
            # remove this cell by setting its label to 0
            labels[cell_mask] = 0
    if in_notebook:
        plt.figure(figsize=(15, 5))
        plt.subplot(131)
        plt.imshow(cell, cmap="inferno")
        plt.axis("off")
        plt.title("cell")
        plt.subplot(132)
        plt.imshow(labels, cmap="nipy_spectral")
        plt.axis("off")
        plt.title("cell masks")
        plt.subplot(133)
        plt.imshow(nuclei_mask, cmap="nipy_spectral")
        plt.axis("off")
        plt.title("nuclei masks")
        plt.show()
    # save the labels
    tifffile.imwrite(nuclei_mask_path, nuclei_mask.astype(np.uint16))
    tifffile.imwrite(labels_path, labels.astype(np.uint16))
