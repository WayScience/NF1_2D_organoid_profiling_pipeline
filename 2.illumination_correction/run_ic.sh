#!/bin/bash

# activate the CellProfiler environment
conda init
conda activate gff_cp_env

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb


cd scripts/ || exit 1

git_root=$(git rev-parse --show-toplevel)
if [ -z "$git_root" ]; then
    echo "Error: Could not find the git root directory."
    exit 1
fi
patients_file="$git_root/data/patient_IDs.txt"
# read patient IDs from the file
mapfile -t patient_array < "$patients_file"


for patient in "${patient_array[@]}"; do
echo "Processing patient: $patient"
    # run Python script for performing illumination correction with CellProfiler
    python cp_illum_correction.py --patient "$patient"
done

conda deactivate

cd ../ || exit 1

echo "Illumination correction completed successfully."
