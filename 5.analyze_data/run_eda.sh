#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ *.ipynb

# run Python script for generating UMAP embeddings
python scripts/0.generate_UMAP_embeddings.py

# Deactivate and activate R conda environment
conda deactivate 
conda activate r_gff_env

# run R script for generating UMAP plots
Rscript scripts/1.vis_UMAP.py
