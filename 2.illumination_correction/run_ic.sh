#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the CellProfiler environment
conda activate gff_cp_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb


cd scripts/ || exit 1

# run Python script for performing illumination correction with CellProfiler
python cp_illum_correction.py

conda deactivate

cd ../ || exit 1

echo "Illumination correction completed successfully."
