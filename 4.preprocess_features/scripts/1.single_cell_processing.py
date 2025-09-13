#!/usr/bin/env python
# coding: utf-8

# # Process single cell profiles

# ## Import libraries

# In[1]:


import argparse
import pathlib
import pprint

import pandas as pd
from pycytominer import aggregate, annotate, feature_select, normalize
from pycytominer.cyto_utils import infer_cp_features

try:
    cfg = get_ipython().config
    in_notebook = True
except NameError:
    in_notebook = False


# In[2]:


if not in_notebook:
    print("Running as script")
    # set up arg parser
    parser = argparse.ArgumentParser(description="Segment the nuclei of a tiff image")

    parser.add_argument(
        "--patient",
        type=str,
        help="Patient ID",
    )

    args = parser.parse_args()
    patient = args.patient
else:
    print("Running in a notebook")
    patient = "NF0014_T1"


# ## Set paths and variables

# In[3]:


# output path for single-cell profiles
output_dir = pathlib.Path(f"../../data/{patient}")
output_dir.mkdir(parents=True, exist_ok=True)
paltemap_path = pathlib.Path(f"../../data/{patient}/platemap/platemap.csv").resolve(
    strict=True
)
# operations to perform for feature selection
feature_select_ops = [
    "variance_threshold",
    "correlation_threshold",
    "blocklist",
    "drop_na_columns",
]


# ## Set dictionary with plates to process

# In[4]:


middle_slice_sc = pathlib.Path(
    f"../../data/{patient}/0.converted/middle_slice_sc.parquet"
).resolve()
max_projected_sc_output = pathlib.Path(
    f"../../data/{patient}/0.converted/max_projected_sc.parquet"
).resolve()
middle_slice_organoid_output = pathlib.Path(
    f"../../data/{patient}/0.converted/middle_slice_organoid.parquet"
).resolve()
max_projected_organoid_output = pathlib.Path(
    f"../../data/{patient}/0.converted/max_projected_organoid.parquet"
).resolve()


# In[5]:


# create plate info dictionary
plate_info_dictionary = {
    "sc_middle_slice": {
        "input_path": pathlib.Path(
            f"../../data/{patient}/0.converted/middle_slice_sc.parquet"
        ).resolve(strict=True),
        "annotated_path": pathlib.Path(
            f"../../data/{patient}/1.annotated/middle_slice_sc.parquet"
        ).resolve(),
        "normalized_path": pathlib.Path(
            f"../../data/{patient}/2.normalized/middle_slice_sc.parquet"
        ).resolve(),
        "feature_selected_path": pathlib.Path(
            f"../../data/{patient}/3.feature_selected/middle_slice_sc.parquet"
        ).resolve(),
        "aggregated_path": pathlib.Path(
            f"../../data/{patient}/4.aggregated/middle_slice_sc.parquet"
        ).resolve(),
    },
    "sc_max_projected": {
        "input_path": pathlib.Path(
            f"../../data/{patient}/0.converted/max_projected_sc.parquet"
        ).resolve(strict=True),
        "annotated_path": pathlib.Path(
            f"../../data/{patient}/1.annotated/max_projected_sc.parquet"
        ).resolve(),
        "normalized_path": pathlib.Path(
            f"../../data/{patient}/2.normalized/max_projected_sc.parquet"
        ).resolve(),
        "feature_selected_path": pathlib.Path(
            f"../../data/{patient}/3.feature_selected/max_projected_sc.parquet"
        ).resolve(),
        "aggregated_path": pathlib.Path(
            f"../../data/{patient}/4.aggregated/max_projected_sc.parquet"
        ).resolve(),
    },
    "organoid_middle_slice": {
        "input_path": pathlib.Path(
            f"../../data/{patient}/0.converted/middle_slice_organoid.parquet"
        ).resolve(strict=True),
        "annotated_path": pathlib.Path(
            f"../../data/{patient}/1.annotated/middle_slice_organoid.parquet"
        ).resolve(),
        "normalized_path": pathlib.Path(
            f"../../data/{patient}/2.normalized/middle_slice_organoid.parquet"
        ).resolve(),
        "feature_selected_path": pathlib.Path(
            f"../../data/{patient}/3.feature_selected/middle_slice_organoid.parquet"
        ).resolve(),
        "aggregated_path": pathlib.Path(
            f"../../data/{patient}/4.aggregated/middle_slice_organoid.parquet"
        ).resolve(),
    },
    "organoid_max_projected": {
        "input_path": pathlib.Path(
            f"../../data/{patient}/0.converted/max_projected_organoid.parquet"
        ).resolve(strict=True),
        "annotated_path": pathlib.Path(
            f"../../data/{patient}/1.annotated/max_projected_organoid.parquet"
        ).resolve(),
        "normalized_path": pathlib.Path(
            f"../../data/{patient}/2.normalized/max_projected_organoid.parquet"
        ).resolve(),
        "feature_selected_path": pathlib.Path(
            f"../../data/{patient}/3.feature_selected/max_projected_organoid.parquet"
        ).resolve(),
        "aggregated_path": pathlib.Path(
            f"../../data/{patient}/4.aggregated/max_projected_organoid.parquet"
        ).resolve(),
    },
}

# view the dictionary to assess that all info is added correctly
pprint.pprint(plate_info_dictionary, indent=4)


# ## Process data with pycytominer

# In[6]:


platemap_df = pd.read_csv(paltemap_path)
for plate, info in plate_info_dictionary.items():
    print(f"Performing pycytominer pipeline for {plate}")
    # make the parent directories for the output files
    for key, value in info.items():
        value.parent.mkdir(parents=True, exist_ok=True)

    profile_df = pd.read_parquet(info["input_path"])

    # Step 1: Annotation
    print("Performing annotation...")
    annotate(
        profiles=profile_df,
        platemap=platemap_df,
        join_on=["Metadata_well_position", "Metadata_Well"],
        output_file=info["annotated_path"],
        output_type="parquet",
    )

    # Load the annotated parquet file to fix metadata columns names
    annotated_df = pd.read_parquet(info["annotated_path"])

    print("Performing normalization...")
    # Step 2: Normalization
    # Find the cp features based on the mask name or image
    if "organoid" in plate.lower():
        compartments = ["Organoid"]
    else:
        compartments = ["Cells", "Nuclei", "Cytoplasm"]
    cp_features = infer_cp_features(
        population_df=annotated_df, compartments=compartments
    )

    # Find the metadata features
    meta_features = infer_cp_features(
        population_df=annotated_df, compartments=compartments, metadata=True
    )

    # Perform normalization
    normalize(
        profiles=annotated_df,
        features=cp_features,
        meta_features=meta_features,
        method="standardize",
        output_file=info["normalized_path"],
        output_type="parquet",
    )

    print("Performing feature selection for...")

    # Step 3: Feature selection
    fs_df = feature_select(
        profiles=str(info["normalized_path"]),
        operation=feature_select_ops,
        na_cutoff=0,
        features=cp_features,
        output_file=str(info["feature_selected_path"]),
        output_type="parquet",
    )

    cp_features = infer_cp_features(
        population_df=pd.read_parquet(info["feature_selected_path"]),
        compartments=compartments,
    )
    fs_df = pd.read_parquet(info["feature_selected_path"])
    # Step 4: Aggregation
    print("Performing aggregation...")
    aggregate(
        population_df=fs_df,
        strata=["Metadata_treatment", "Metadata_dose"],
        features=cp_features,
        operation="median",
        output_file=str(info["aggregated_path"]),
        output_type="parquet",
    )
    print(f"Aggregation has been performed for:\n{plate}")
