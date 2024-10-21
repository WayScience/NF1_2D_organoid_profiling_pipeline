#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebook(s) to script
jupyter nbconvert --to script --output-dir=scripts/ *.ipynb

# # run Python script for upating image file structure
python scripts/update_file_structure.py

# Deactivate environment and activate R environment
conda deactivate
conda activate r_gff_env

# Change into the metadata directory
cd metadata

# convert Jupyter notebook(s) to script
jupyter nbconvert --to script --output-dir=scripts/ *.ipynb

# run R script to generate platemaps
Rscript -e ".libPaths('/home/jenna/mambaforge/envs/r_gff_env/lib/R/library'); source('scripts/platemap_vis.r')"
