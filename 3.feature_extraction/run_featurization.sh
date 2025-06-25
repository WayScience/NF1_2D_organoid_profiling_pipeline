#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_cellprofiler

# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

cd scripts/ || exit

patient="NF0014"
z_stack_dir="../../data/$patient/zstack_images"

mapfile -t well_fovs < <(ls -d "$z_stack_dir"/*)

total_dirs=$(echo "${well_fovs[@]}" | wc -w)
echo "Total directories: $total_dirs"
# loop through all input directories
for well_fov in "${well_fovs[@]}"; do
    well_fov=${well_fov%*/}
    well_fov=$(basename "$well_fov")
    echo "Processing well_fov: $well_fov"

    python cp_analysis.py \
        --patient "$patient" \
        --well_fov "$well_fov"

done

cd ../ || exit

conda deactivate

echo "Cell segmentation preprocessing completed successfully."
