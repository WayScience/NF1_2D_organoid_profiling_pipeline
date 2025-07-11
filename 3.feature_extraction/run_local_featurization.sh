#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_cellprofiler

git_root=$(git rev-parse --show-toplevel)
if [ -z "$git_root" ]; then
    echo "Error: Could not find the git root directory."
    exit 1
fi

patients_file="$git_root/data/patient_IDs.txt"
# read patient IDs from the file
mapfile -t patients < "$patients_file"

total_patients=${#patients[@]}
patient_counter=0

echo "Starting feature extraction for $total_patients patients..."
echo "========================================="

for patient in "${patients[@]}"; do
    ((patient_counter++))

    z_stack_dir="$git_root/data/$patient/zstack_images"

    mapfile -t well_fovs < <(ls -d "$z_stack_dir"/*)

    total_tasks=${#well_fovs[@]}
    echo "[$patient_counter/$total_patients] Processing patient: $patient"

    well_fov_counter=0

    total_dirs=$(echo "${well_fovs[@]}" | wc -w)
    echo "Total directories: $total_dirs"
    # loop through all input directories
    for well_fov in "${well_fovs[@]}"; do
        ((well_fov_counter++))

        well_fov=${well_fov%*/}
        well_fov=$(basename "$well_fov")
        echo "Processing well_fov: $well_fov"
        progress=$((well_fov_counter * 100 / total_tasks))
        echo "    [$well_fov_counter/$total_tasks] ($progress%) Processing $well_fov method..."


        python "$git_root"/3.feature_extraction/scripts/cp_analysis.py \
            --patient "$patient" \
            --well_fov "$well_fov"

        echo "  ✓ Completed well_fov: $well_fov"

    done
    echo "✓ [$patient_counter/$total_patients] Completed processing for patient: $patient"
    echo "-----------------------------------------"
done


conda deactivate

echo "Cell segmentation preprocessing completed successfully."
