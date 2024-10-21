#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ *.ipynb

# run Python script for checking for incomplete sets and cleaning
python scripts/0.check_incomplete_sets.py

# deactivate preprocessing env and activate CellProfiler env
conda deactivate
conda activate gff_cp_env

# run Python script for performing max-projection with CellProfiler
python scripts/1.cp_max_projection.py
