#!/bin/bash

module load anaconda
# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation

cd scripts/ || exit

patient=$1
well_fov=$2

echo "Performing segmentation for patient: $patient, well_fov: $well_fov"

twoD_methods=( "zmax" "middle" )

for twoD_method in "${twoD_methods[@]}"; do
    echo "Processing well_fov: $well_fov with twoD_method: $twoD_method"
    # run Python script for running segmentation of compartments
    python 0.segment_nuclei.py \
        --patient "$patient" \
        --well_fov "$well_fov" \
        --clip_limit 0.03 \
        --twoD_method "$twoD_method"
    python 1.segment_cells.py \
        --patient "$patient" \
        --well_fov "$well_fov" \
        --clip_limit 0.01 \
        --twoD_method "$twoD_method"
    python 2.segment_organoids.py \
        --patient "$patient" \
        --well_fov "$well_fov" \
        --clip_limit 0.01 \
        --twoD_method "$twoD_method"
done

cd ../ || exit

conda deactivate

echo "Cell segmentation preprocessing completed successfully."
