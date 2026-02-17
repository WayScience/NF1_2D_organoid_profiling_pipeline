#!/usr/bin/env python
# coding: utf-8

# This notebook focuses on trying to find a way to segment cells within organoids properly.
# The end goals is to segment cell and extract morphology features from cellprofiler.
# These masks must be imported into cellprofiler to extract features.

# In[1]:


import os
import pathlib
import warnings

import imageio.v3 as iio
import matplotlib.patches as patches
import matplotlib.pyplot as plt

# Import dependencies
import numpy as np
import scipy
import scipy as sp
import skimage
import tifffile
import torch
from arg_parsing_utils import check_for_missing_args, parse_args
from cellpose import models
from notebook_init_utils import bandicoot_check, init_notebook
from skimage import io

# from cellSAM import cellsam_pipeline, get_model
# from cellSAM.utils import format_image_shape, normalize_image


root_dir, in_notebook = init_notebook()
image_base_dir = bandicoot_check(
    pathlib.Path(os.path.expanduser("~/mnt/bandicoot")).resolve(), root_dir
)


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
    patient = "NF0014_T2"
    well_fov = "C4-6"
    clip_limit = 0.03
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

labels_path = input_dir / f"{well_fov}_organoid_masks.tiff"
mask_path = input_dir


# ## Set up images, paths and functions

# In[3]:


if overwrite or not labels_path.exists():
    image_extensions = {".tif", ".tiff"}
    files = sorted(input_dir.glob("*"))
    files = [str(x) for x in files if x.suffix in image_extensions]
    # find the cytoplasmic channels in the image set
    for f in files:
        if "405" in f:
            nuc = io.imread(f)
        elif "488" in f:
            cyto1 = io.imread(f)
        elif "555" in f:
            cyto2 = io.imread(f)
        elif "640" in f:
            cyto3 = io.imread(f)

    cyto = np.maximum(
        cyto1,
        cyto2,
    )


# In[4]:


# supress warning
warnings.filterwarnings(
    "ignore",
    message="Low IOU threshold, ignoring mask.",
    category=UserWarning,
    module="cellSAM.sam_inference",
)


# organoid_mask = cellsam_pipeline(
#     cyto,
#     use_wsi=False,
#     low_contrast_enhancement=False,
#     gauge_cell_size=False,
# )
use_GPU = torch.cuda.is_available()
# Load the model
model = models.CellposeModel(gpu=use_GPU)
organoid_mask, details, _ = model.eval(cyto)


organoid_mask[organoid_mask > 0] = 1
organoid_mask = scipy.ndimage.binary_fill_holes(organoid_mask)
organoid_mask = scipy.ndimage.label(organoid_mask)[0]
tifffile.imwrite(labels_path, organoid_mask.astype(np.uint16))

if in_notebook:
    # Visualize results
    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.imshow(cyto, cmap="inferno")
    plt.title("Cyto Slice")
    plt.axis("off")
    plt.subplot(122)
    plt.imshow(organoid_mask, cmap="nipy_spectral")
    plt.title("CellSAM Segmentation Mask")
    plt.axis("off")
    plt.show()
