#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pathlib
import sys

import tifffile
import tqdm

# check if in a jupyter notebook
try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False


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

from parsable_args import parse_featurization_args_patient

# In[2]:


if not in_notebook:
    args_dict = parse_featurization_args_patient()
    patient = args_dict["patient"]
else:
    patient = "NF0014"


# In[ ]:


# input images directory
images_dir = pathlib.Path(f"{root_dir}/data/{patient}/zstack_images/").resolve(
    strict=True
)
# output images directory
output_dir = pathlib.Path(f"{root_dir}/data/{patient}/middle_slice/").resolve()


# In[4]:


# get a list of all of the tiff files in the directory
tiff_files = list(images_dir.rglob("*.tif"))
tiff_files.sort()
for tiff_file in tqdm.tqdm(tiff_files):
    # load the first tiff file to get the metadata
    image = tifffile.TiffFile(tiff_file)
    number_of_slices = image.series[0].shape[0]
    # get the middle most slice
    middle_slice_index = number_of_slices // 2
    # get the middle slice
    middle_slice = image.series[0].asarray()[middle_slice_index, :, :]
    # save the middle slice as a new tiff file
    output_file_dir = output_dir / str(tiff_file.parent).split("/")[-1] / tiff_file.name
    output_file_dir.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(output_file_dir, middle_slice)
