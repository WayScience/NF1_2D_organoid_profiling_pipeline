#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

cd scripts || exit
# run Python script for checking for incomplete sets and cleaning
python 0.cp_max_projection.py
python 1.get_the_middle_slice.py

conda deactivate

cd .. || exit

echo "All scripts executed successfully."
