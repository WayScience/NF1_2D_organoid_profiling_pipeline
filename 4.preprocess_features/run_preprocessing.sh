#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

cd scripts/ || exit
patient_array=( "NF0014_T1" "NF0016_T1" "NF0018_T6" "NF0021_T1" "NF0030_T1" "NF0040_T1" "SARCO219_T2" "SARCO361_T1" )
# patient_array=( "SARCO219_T2" "SARCO361_T1" )

for patient in "${patient_array[@]}"; do
    echo "Processing patient: $patient"

    # run Python script for running preprocessing of morphology profiles
    python 0.convert_cytotable.py --patient "$patient"
    python 1.single_cell_processing.py --patient "$patient"

done

cd ../ || exit

