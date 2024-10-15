#!/usr/bin/env python
# coding: utf-8

# # Copy raw images into one folder to use for CellProfiler processing
# 
# Currently, the images are located nest deep within multiple folders. 
# For best practices, we will copy the images (preserving metadata) to one folder that can be used for CellProfiler processing.

# ## Import libraries

# In[1]:


from pathlib import Path
import shutil


# ## Set paths and variables

# In[2]:


# Define the parent directory containing all the nested folders
parent_dir = Path(
    "/media/18tbdrive/GFF_organoid_data/Cell Painting-NF0014 Thawed3-Pilot Drug Screening/NF0014-Thawed 3 (Raw image files)-Combined/NF0014-Thawed 3 (Raw image files)-Combined copy"
).resolve(strict=True)

# Create the NF0014 folder next to the parent_dir (same level in the hierarchy)
nf0014_dir = parent_dir.parent / "NF0014"
nf0014_dir.mkdir(exist_ok=True)

# Image extensions that we are looking to copy
image_extensions = {".tif", ".tiff"}


# ## Reach the nested images and copy to one folder

# In[3]:


# Iterate over all folders at the first level inside the parent directory
for first_level_folder in parent_dir.iterdir():
    if first_level_folder.is_dir():
        # Go into the first folder
        for second_level_folder in first_level_folder.iterdir():
            if second_level_folder.is_dir():
                # Go into the second folder
                for third_level_folder in second_level_folder.iterdir():
                    if third_level_folder.is_dir():
                        # Get all images inside the third-level folder
                        for image_file in third_level_folder.iterdir():
                            if image_file.suffix.lower() in image_extensions:
                                # Copy each image to the NF0014 folder
                                destination = nf0014_dir / image_file.name
                                shutil.copy2(image_file, destination)  # copy2 preserves metadata

print("All images have been copied to the NF0014 folder!")

