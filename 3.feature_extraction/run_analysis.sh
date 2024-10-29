#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the CellProfiler environment
conda activate gff_cp_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ *.ipynb

# run Python script for performing illumination correction with CellProfiler
python scripts/cp_analysis.py
