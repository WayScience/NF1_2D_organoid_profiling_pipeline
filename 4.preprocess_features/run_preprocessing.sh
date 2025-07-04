#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

patient="NF0014"
cd scripts/ || exit
# run Python script for running preprocessing of morphology profiles
python 0.convert_cytotable.py --patient "$patient"
python 1.single_cell_processing.py --patient "$patient"

cd ../ || exit

