#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

overwrite="TRUE"

git_root=$(git rev-parse --show-toplevel)
if [ -z "$git_root" ]; then
    echo "Error: Could not find the git root directory."
    exit 1
fi

patients_file="$git_root/data/patient_IDs.txt"
# read patient IDs from the file
mapfile -t patients < "$patients_file"

bandicoot_path="${HOME}/mnt/bandicoot/NF1_organoid_data/"

# if bandicoot path exists, set the data path to bandicoot
if [ -d "$bandicoot_path" ]; then
    echo "Bandicoot path found. Setting data path to Bandicoot."
    git_root="$bandicoot_path"
else
    echo "Bandicoot path not found. Using local git repository data path."
fi

mkdir -p "logs"

total_patients=${#patients[@]}
patient_counter=0

echo "Starting cell segmentation for $total_patients patients..."
echo "========================================="

patients=( "NF0014_T1" )

for patient in "${patients[@]}"; do
    ((patient_counter++))
    z_stack_dir="$git_root/data/$patient/zstack_images"

    mapfile -t well_fovs < <(ls -d "$z_stack_dir"/*)

    total_dirs=${#well_fovs[@]}
    echo "[$patient_counter/$total_patients] Processing patient: $patient"
    echo "  Found $total_dirs well_fovs to process"

    twoD_methods=( "zmax" "middle" "middle_n" )
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
        log_file="logs/segment_organoids_${patient}_${well_fov}.log"
        if [ -f "$log_file" ]; then
            rm "$log_file"
        fi
        mkdir -p "$(dirname "$log_file")"
        touch "$log_file"

        for twoD_method in "${twoD_methods[@]}"; do
            ((task_counter++))

            # Calculate progress percentage
            progress=$((task_counter * 100 / total_tasks))

            echo "    [$task_counter/$total_tasks] ($progress%) Processing $twoD_method method..."

            # run Python script for running preprocessing of morphology profiles
            {
                echo "=== Starting segmentation pipeline for $patient - $well_fov - $twoD_method at $(date) ==="

                if [ $overwrite = "TRUE" ] ; then
                    echo "Step 1/3: Nuclei segmentation..."
                    python -u scripts/0.segment_nuclei.py \
                        --patient "$patient" \
                        --well_fov "$well_fov" \
                        --clip_limit 0.03 \
                        --twoD_method "$twoD_method" \
                        --overwrite
                    echo "✓ Nuclei segmentation completed"

                    echo "Step 2/3: Cell segmentation..."
                    python scripts/1.segment_cells.py \
                        --patient "$patient" \
                        --well_fov "$well_fov" \
                        --clip_limit 0.01 \
                        --twoD_method "$twoD_method" \
                        --overwrite
                    echo "✓ Cell segmentation completed"

                    echo "Step 3/3: Organoid segmentation..."
                    python scripts/2.segment_organoids.py \
                        --patient "$patient" \
                        --well_fov "$well_fov" \
                        --clip_limit 0.01 \
                        --twoD_method "$twoD_method" \
                        --overwrite
                    echo "✓ Organoid segmentation completed"
                else
                    echo "Step 1/3: Nuclei segmentation..."
                    python -u scripts/0.segment_nuclei.py \
                        --patient "$patient" \
                        --well_fov "$well_fov" \
                        --clip_limit 0.03 \
                        --twoD_method "$twoD_method"
                    echo "✓ Nuclei segmentation completed"

                    echo "Step 2/3: Cell segmentation..."
                    python scripts/1.segment_cells.py \
                        --patient "$patient" \
                        --well_fov "$well_fov" \
                        --clip_limit 0.01 \
                        --twoD_method "$twoD_method"
                    echo "✓ Cell segmentation completed"

                    echo "Step 3/3: Organoid segmentation..."
                    python scripts/2.segment_organoids.py \
                        --patient "$patient" \
                        --well_fov "$well_fov" \
                        --clip_limit 0.01 \
                        --twoD_method "$twoD_method"
                    echo "✓ Organoid segmentation completed"

                echo "=== Completed segmentation pipeline at $(date) ==="
                echo ""
                fi
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
