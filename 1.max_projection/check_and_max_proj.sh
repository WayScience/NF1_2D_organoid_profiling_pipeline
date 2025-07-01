#!/bin/bash

git_root=$(git rev-parse --show-toplevel)
if [ -z "$git_root" ]; then
    echo "Error: Could not find the git root directory."
    exit 1
fi

#  read in the patients as array
patient_array_file_path="$git_root/data/patient_IDs.txt"
# read the patient IDs from the file into an array
if [[ -f "$patient_array_file_path" ]]; then
    readarray -t patient_array < "$patient_array_file_path"
else
    echo "Error: File $patient_array_file_path does not exist."
    exit 1
fi

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate gff_preprocessing_env


# run Python script for checking for incomplete sets and cleaning
for patient in "${patient_array[@]}"; do
    echo "Processing patient: $patient"
    python 0.cp_max_projection.py --patient "$patient"
    python 1.get_the_middle_slice.py --patient "$patient"
done

conda deactivate


echo "All scripts executed successfully."
