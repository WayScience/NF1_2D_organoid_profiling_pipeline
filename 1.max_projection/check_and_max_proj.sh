#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

cd scripts || exit

patient_array=( "NF0014" "NF0016" "NF0018" "NF0021" "NF0030" "NF0040" "SARCO219" "SARCO361" )

for patient in "${patient_array[@]}"; do
    # run Python script for checking for incomplete sets and cleaning
    python 0.cp_max_projection.py --patient "$patient"
    python 1.get_the_middle_slice.py --patient "$patient"
done

conda deactivate

cd .. || exit

echo "All scripts executed successfully."
