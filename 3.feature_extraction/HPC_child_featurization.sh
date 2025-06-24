#!/bin/bash

module load anaconda
# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation

cd scripts/ || exit

patient=$1
well_fov=$2

echo "Performing featurization for patient: $patient, well_fov: $well_fov"

python cp_analysis.py \
    --patient "$patient" \
    --well_fov "$well_fov"

cd ../ || exit

conda deactivate

echo "Featurization completed successfully."
