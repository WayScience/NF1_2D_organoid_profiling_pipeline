#!/usr/bin/env python
# coding: utf-8

# # Process single cell profiles

# ## Import libraries

# In[1]:


import pathlib
import pprint

import pandas as pd

from pycytominer import annotate, normalize, feature_select
from pycytominer.cyto_utils import infer_cp_features


# ## Set paths and variables

# In[2]:


# Path to dir with profiles
profiles_dir = pathlib.Path("./data/converted_profiles")

# output path for single-cell profiles 
output_dir = pathlib.Path("./data/single_cell_profiles")
output_dir.mkdir(parents=True, exist_ok=True)

# Extract the plate names from the file name
plate_names = [file.stem.split("_")[0] for file in profiles_dir.glob("*.parquet")]

# path for platemap directory
platemap_dir = pathlib.Path("../0.download_data/metadata")

# operations to perform for feature selection
feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns"
]


# ## Set dictionary with plates to process

# In[3]:


# create plate info dictionary 
plate_info_dictionary = {
    name: {
        "profile_paths": {
            "sc": str(
                pathlib.Path(list(profiles_dir.rglob(f"{name}_sc_converted.parquet"))[0]).resolve(
                    strict=True
                )
            ),
            "organoid": str(
                pathlib.Path(list(profiles_dir.rglob(f"{name}_organoid_converted.parquet"))[0]).resolve(
                    strict=True
                )
            ),
        },
        "platemap_path": str(
            pathlib.Path(list(platemap_dir.rglob(f"{name}_platemap.csv"))[0]).resolve(
                strict=True
            )
        ),
    }
    for name in plate_names
}

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Process data with pycytominer

# In[4]:


for plate, info in plate_info_dictionary.items():
    print(f"Performing pycytominer pipeline for {plate}")

    # Prepare output paths for different profile types
    for profile in ["sc", "organoid"]:
        output_annotated_file = str(pathlib.Path(f"{output_dir}/{plate}_{profile}_annotated.parquet"))
        output_normalized_file = str(pathlib.Path(f"{output_dir}/{plate}_{profile}_normalized.parquet"))
        output_feature_select_file = str(pathlib.Path(f"{output_dir}/{plate}_{profile}_feature_selected.parquet"))
        
        profile_path = info["profile_paths"].get(profile)

        if profile_path:
            # Read in the profile and platemap files
            profile_df = pd.read_parquet(profile_path)
            platemap_df = pd.read_csv(info["platemap_path"])

            # Set compartments based on profile type
            compartments = ["nuclei", "cells", "cytoplasm"] if profile == "sc" else ["organoid"]

            print("Performing annotation for", plate, "for the", profile, "profiles...")

            # Step 1: Annotation
            annotate(
                profiles=profile_df,
                platemap=platemap_df,
                join_on=["Metadata_well_position", "Image_Metadata_Well"],
                output_file=output_annotated_file,
                output_type="parquet",
            )

            # Load the annotated parquet file to fix metadata columns names
            annotated_df = pd.read_parquet(output_annotated_file)

            # Rename columns using the rename() function
            column_name_mapping = {
                "Image_Metadata_Site": "Metadata_Site",
                "Image_Metadata_ZSlice": "Metadata_ZSlice"
            }

            annotated_df.rename(columns=column_name_mapping, inplace=True)

            # Save the modified DataFrame back to the same location
            annotated_df.to_parquet(output_annotated_file, index=False)
            
            print("Performing normalization...")

            # Step 2: Normalization
            # Find the cp features based on the mask name or image
            cp_features = infer_cp_features(population_df=annotated_df, compartments=compartments)

            # Find the metadata features
            meta_features = infer_cp_features(population_df=annotated_df, compartments=compartments, metadata=True)

            # Perform normalization
            normalize(
                profiles=annotated_df,
                features=cp_features,
                meta_features=meta_features,
                method="standardize",
                output_file=output_normalized_file,
                output_type="parquet",
            )
            
            print("Performing feature selection for...")

            # Step 3: Feature selection
            feature_select(
                profiles=output_normalized_file,
                operation=feature_select_ops,
                na_cutoff=0,
                features=cp_features,
                output_file=output_feature_select_file,
                output_type="parquet"
            )
            print(f"Annotation, normalization, and feature selection have been performed for {plate} and {profile} profiles")

        else:
            print(f"{profile.capitalize()} profile path not found for {plate}")


# In[5]:


# Check output file
test_df = pd.read_parquet(output_feature_select_file)

print(test_df.shape)
test_df.head(2)

