#!/bin/bash

# This script runs all the modules in one fell swooop
# Change the module values to TRUE/FALSE to run or skip specific modules
# This is for a local caller, not for a cluster environment


DOWNLOAD=FALSE
PREPROCESS=FALSE
ILLUMINATION_CORRECTION=FALSE
SEGMENT=TRUE
EXTRACT_FEATURES=FALSE
IMAGE_BASED_PROFILING=FALSE
ANALYSIS=FALSE

##################################
# Place holder for data download / streaming
####################################
if [ "$DOWNLOAD" = TRUE ] ; then
    echo "Running Data Download Module..."
    # bash 0.data_download/run_data_download.sh
    echo "Data Download Module is not yet implemented."
else
    echo "Skipping Data Download Module..."
fi

##################################
# Preprocessing
# Maximum intensity projection
##################################
if [ "$PREPROCESS" = TRUE ] ; then
    echo "Running Preprocessing Module..."
    cd 1.max_projection || exit
    source check_and_max_proj.sh
    cd .. || exit
else
    echo "Skipping Preprocessing Module..."
fi

####################################
# Illumination correction
####################################
if [ "$ILLUMINATION_CORRECTION" = TRUE ] ; then
    echo "Running Illumination Correction Module..."
    cd 2.illumination_correction || exit
    source run_ic.sh
    cd .. || exit
else
    echo "Skipping Illumination Correction Module..."
fi

##################################
# Cell Segmentation
##################################
if [ "$SEGMENT" = TRUE ] ; then
    echo "Running Cell Segmentation Module..."
    bash 3.cell_segmentation/run_segmentation.sh
else
    echo "Skipping Cell Segmentation Module..."
fi

##################################
# Feature Extraction
##################################
if [ "$EXTRACT_FEATURES" = TRUE ] ; then
    echo "Running Feature Extraction Module..."
    bash 3.feature_extraction/run_local_featurization.sh
else
    echo "Skipping Feature Extraction Module..."
fi


##################################
# Image-based Profiling
##################################
if [ "$IMAGE_BASED_PROFILING" = TRUE ] ; then
    echo "Running Image-based Profiling Module..."
    bash 4.preprocess_features/run_preprocessing.sh
else
    echo "Skipping Image-based Profiling Module..."
fi


##################################
# Analysis
##################################
if [ "$ANALYSIS" = TRUE ] ; then
    echo "Running Analysis Module..."
    bash 5.analyze_data/run_eda.sh
else
    echo "Skipping Analysis Module..."
fi
