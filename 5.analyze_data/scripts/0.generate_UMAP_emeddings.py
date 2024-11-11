#!/usr/bin/env python
# coding: utf-8

# # Generate UMAP embeddings per plate and profile (single-cell or organoid)

# In[1]:


import glob
import pathlib
import pandas as pd
import umap

from pycytominer import feature_select
from pycytominer.cyto_utils import infer_cp_features


# ## Set paths and constants

# In[2]:


# Set constants
umap_random_seed = 0
umap_n_components = 2

output_dir = pathlib.Path("results")
output_dir.mkdir(parents=True, exist_ok=True)


# ## Identify file paths to process

# In[3]:


# Set input paths
data_dir = pathlib.Path("../4.preprocess_features/data/single_cell_profiles")

# Select only the feature selected files
file_suffix = "*feature_selected.parquet"

# Obtain file paths for all feature selected plates
fs_files = glob.glob(f"{data_dir}/{file_suffix}")
fs_files


# In[4]:


# Load feature data into a dictionary, keyed on plate name
cp_dfs = {x.split("/")[-1]: pd.read_parquet(x) for x in fs_files}

# Print out useful information about each dataset
print(cp_dfs.keys())
[cp_dfs[x].shape for x in cp_dfs]


# In[5]:


desired_columns = [
    "Metadata_Plate",
    "Metadata_Well",
    "Metadata_Site",
    "Metadata_treatment",
    "Metadata_dose",
    "Metadata_ZSlice",
    "Metadata_Nuclei_Location_Center_X",
    "Metadata_Nuclei_Location_Center_Y",
]

# Fit UMAP features per dataset and save
for plate in cp_dfs:
    # Extract the first two parts of the plate name
    plate_name_parts = pathlib.Path(plate).stem.split("_")[:2]
    plate_name = "_".join(plate_name_parts)
    print("UMAP embeddings being generated for", plate_name)

    # Set compartments based on the second part of the plate name
    compartments = [
        compartment for profile_type, compartment in [
            ("sc", ["nuclei", "cells", "cytoplasm"]),
            ("organoid", ["organoids"])
        ] if plate_name_parts[1] == profile_type
    ]

    # Continue with UMAP processing
    umap_fit = umap.UMAP(random_state=umap_random_seed, n_components=umap_n_components, n_jobs=1)

    # Select one plate at a time to process
    cp_df = cp_dfs[plate]

    # Separate feature versus metadata
    cp_features = infer_cp_features(cp_df, compartments=compartments)
    meta_features = infer_cp_features(cp_df, metadata=True, compartments=compartments)
    filtered_meta_features = [
        feature for feature in meta_features if feature in desired_columns
    ]

    # Confirms that no NA columns are included
    cp_df = feature_select(
        cp_dfs[plate], features=cp_features, operation="drop_na_columns", na_cutoff=0
    )

    embeddings = pd.DataFrame(
        umap_fit.fit_transform(cp_df.loc[:, cp_features]),
        columns=[f"UMAP{x}" for x in range(0, umap_n_components)],
    )
    print(embeddings.shape)

    cp_umap_with_metadata_df = pd.concat(
        [cp_df.loc[:, filtered_meta_features].reset_index(drop=True), embeddings],
        axis=1,
    )
    cp_umap_with_metadata_df = cp_umap_with_metadata_df.sample(frac=1, random_state=0)

    output_umap_file = pathlib.Path(output_dir, f"UMAP_{plate_name}.tsv")
    cp_umap_with_metadata_df.to_csv(output_umap_file, index=False, sep="\t")


# In[6]:


# Print an example output file
print(cp_umap_with_metadata_df.shape)
cp_umap_with_metadata_df.head(10)

