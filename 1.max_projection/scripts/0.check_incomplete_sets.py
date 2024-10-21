#!/usr/bin/env python
# coding: utf-8

# ##

# # Check the directory of images for any incomplete z-slice channel sets (unique well, site, and z-slice)
# 
# Prior to processing with CellProfiler to perform max-projection which creates image sets (unique well and site) using the maximum pixel across multiple z-slices.
# In this notebook, we check to confirm that there all complete z-slice channel sets (all channels per well/site/z-slice).
# If there are any incomplete, we move them out into a new folder called "incomplete_data" to avoid issues with CellProfiler being super mad that are any missing channels.

# ## Import libraries

# In[1]:


import shutil
from pathlib import Path
from collections import defaultdict


# ## Set paths and variables

# In[2]:


# Define the path to your directory containing the images
image_dir = Path("/media/18tbdrive/GFF_organoid_data/Cell Painting-NF0014 Thawed3-Pilot Drug Screening/NF0014-Thawed 3 (Raw image files)-Combined/NF0014")

# Initialize a dictionary to store channels for each unique image set
image_sets = defaultdict(set)


# ## Evaluate if there are incomplete z-slice channel sets or not

# In[3]:


from collections import defaultdict
from pathlib import Path

# Assuming image_dir is defined as the directory containing the TIFF files
# Define the required channels
required_channels = {'640', '405', '555'}  # Add other required channels as needed

# Initialize a dictionary to hold sets of channels for each image set
image_sets = defaultdict(set)

# Loop through all TIFF files in the directory
for image_file in image_dir.glob("*.tif"):
    # Split the filename to extract key information
    parts = image_file.stem.split("_")

    # Extract well and site (e.g., 'C10-1' -> well='C10', site='1')
    well_site = parts[0]
    well = well_site.split("-")[0]  # Extract well (e.g., 'C10')
    site = well_site.split("-")[1]  # Extract site (e.g., '1')

    # Extract Z-slice identifier (e.g., ZS000)
    z_slice = parts[2]  # Example: 'ZS000'

    # Create a unique identifier for the image set (well, site, Z-slice)
    set_id = f"{well}_site{site}_{z_slice}"

    # Store the channel for this image set
    channel = parts[1]
    image_sets[set_id].add(channel)

# Find image sets missing any required channels
missing_channels = []

for set_id, channels in image_sets.items():
    # Check which required channels are missing
    missing = required_channels - channels
    if missing:
        missing_channels.append((set_id, missing))  # Store set_id with missing channels

# Print the results
if missing_channels:
    print("The following image sets are missing one or more required channels:")
    for set_id, missing in missing_channels:
        print(f"{set_id} is missing channel(s): {', '.join(missing)}")
else:
    print("All image sets contain the required channels.")


# ## If there are any incomplete sets, move them into a separate directory called `incomplete_data`

# In[4]:


# Define the path for the incomplete data directory
incomplete_data_dir = image_dir.parent / 'incomplete_data'

# Create the incomplete_data directory if it doesn't exist
incomplete_data_dir.mkdir(exist_ok=True)

# Move the files corresponding to the missing channels
for set_id, missing in missing_channels:  # Unpack the tuple
    # Extract well and site from set_id
    well_site_parts = set_id.split('_site')  # Split into well and site
    if len(well_site_parts) == 2:  # Ensure it has two parts
        well = well_site_parts[0]  # Get well part
        site_z = well_site_parts[1]  # Get site and z-slice part
        site, z_slice = site_z.split('_')  # Now split the site and z-slice
    else:
        print(f"Unexpected set_id format: {set_id}")
        continue  # Skip this set_id if format is unexpected

    # Loop through the image files again to find those to move
    for file in image_dir.glob("*.tif"):
        if f"{well}-{site}" in file.stem and z_slice in file.stem:
            # Define the target path in the incomplete_data directory
            target_path = incomplete_data_dir / file.name
            # Move the file to the incomplete_data directory
            shutil.move(str(file), str(target_path))
            print(f"Moved: {file} to {target_path}")

