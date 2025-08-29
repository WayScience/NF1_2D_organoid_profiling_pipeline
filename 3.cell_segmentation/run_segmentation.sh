#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation

git_root=$(git rev-parse --show-toplevel)
if [ -z "$git_root" ]; then
    echo "Error: Could not find the git root directory."
    exit 1
fi

patients_file="$git_root/data/patient_IDs.txt"
# read patient IDs from the file
mapfile -t patients < "$patients_file"

mkdir -p "$git_root/3.cell_segmentation/logs"

total_patients=${#patients[@]}
patient_counter=0

echo "Starting cell segmentation for $total_patients patients..."
echo "========================================="

for patient in "${patients[@]}"; do
    ((patient_counter++))
    z_stack_dir="$git_root/data/$patient/zstack_images"

    mapfile -t well_fovs < <(ls -d "$z_stack_dir"/*)

    total_dirs=${#well_fovs[@]}
    echo "[$patient_counter/$total_patients] Processing patient: $patient"
    echo "  Found $total_dirs well_fovs to process"

    twoD_methods=( "zmax" "middle" )
    well_fov_counter=0

    # Calculate total tasks for this patient
    total_tasks=$((total_dirs * ${#twoD_methods[@]}))
    task_counter=0

    # loop through all input directories
    for well_fov in "${well_fovs[@]}"; do
        ((well_fov_counter++))
        well_fov=${well_fov%*/}
        well_fov=$(basename "$well_fov")

        echo "  [$well_fov_counter/$total_dirs] Processing well_fov: $well_fov"

        # create the log file
        log_file="$git_root/3.cell_segmentation/logs/segment_organoids_${patient}_${well_fov}.log"
        if [ -f "$log_file" ]; then
            rm "$log_file"
        fi
        touch "$log_file"

        for twoD_method in "${twoD_methods[@]}"; do
            ((task_counter++))

            # Calculate progress percentage
            progress=$((task_counter * 100 / total_tasks))

            echo "    [$task_counter/$total_tasks] ($progress%) Processing $twoD_method method..."

            # run Python script for running preprocessing of morphology profiles
            {
                echo "=== Starting segmentation pipeline for $patient - $well_fov - $twoD_method at $(date) ==="

                echo "Step 1/3: Nuclei segmentation..."
                python -u "$git_root"/3.cell_segmentation/scripts/0.segment_nuclei.py \
                    --patient "$patient" \
                    --well_fov "$well_fov" \
                    --clip_limit 0.03 \
                    --twoD_method "$twoD_method"
                echo "✓ Nuclei segmentation completed"

                echo "Step 2/3: Cell segmentation..."
                python "$git_root"/3.cell_segmentation/scripts/1.segment_cells.py \
                    --patient "$patient" \
                    --well_fov "$well_fov" \
                    --clip_limit 0.01 \
                    --twoD_method "$twoD_method"
                echo "✓ Cell segmentation completed"

                echo "Step 3/3: Organoid segmentation..."
                python "$git_root"/3.cell_segmentation/scripts/2.segment_organoids.py \
                    --patient "$patient" \
                    --well_fov "$well_fov" \
                    --clip_limit 0.01 \
                    --twoD_method "$twoD_method"
                echo "✓ Organoid segmentation completed"

                echo "=== Completed segmentation pipeline at $(date) ==="
                echo ""
            } >> "$log_file" 2>&1

            echo "    ✓ Completed $twoD_method method"
        done
        echo "  ✓ Completed well_fov: $well_fov"
    done
    echo "✓ [$patient_counter/$total_patients] Completed processing for patient: $patient"
    echo "-----------------------------------------"
done


conda deactivate

echo ""
echo "========================================="
echo "✓ Cell segmentation preprocessing completed successfully!"
echo "Processed $total_patients patients with all well_fovs and methods."
echo "Check logs in: $git_root/3.cell_segmentation/logs/"
