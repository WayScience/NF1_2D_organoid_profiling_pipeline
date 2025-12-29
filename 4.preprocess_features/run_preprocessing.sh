#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

cd scripts/ || exit
patient_array_file_path="../data/patient_IDs.txt"
readarray -t patient_array < "$patient_array_file_path"

for patient in "${patient_array[@]}"; do
    echo "Processing patient: $patient"
    # run Python script for running preprocessing of morphology profiles
    python 0.convert_cytotable.py --patient "$patient"
    python 1.single_cell_processing.py --patient "$patient"
done

python 2.combine_patients.py

cd ../ || exit

