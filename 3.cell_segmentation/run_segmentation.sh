#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

overwrite="FALSE"
twoD_methods=( "zmax" "middle" "middle_n" )
input_file="loadfiles/segmentation_loadfile.txt"

mkdir -p "logs"
patient_well_fov_counter=0
# get the number of lines in the input file
total_lines=$(wc -l < "$input_file")

while IFS= read -r line; do
    ((patient_well_fov_counter++))

    # split the line into an array
    IFS=$'\t' read -r -a parts <<< "$line"

    patient="${parts[0]}"
    well_fov="${parts[1]}"

    echo "  [$patient_well_fov_counter/$total_lines] Processing $patient - $well_fov"

    # create the log file
    log_file="logs/segment_organoids_${patient}_${well_fov}.log"
    if [ -f "$log_file" ]; then
        rm "$log_file"
    fi
    mkdir -p "$(dirname "$log_file")"
    touch "$log_file"

    for twoD_method in "${twoD_methods[@]}"; do
    # run Python script for running preprocessing of morphology profiles
        if [ $overwrite = "TRUE" ] ; then
            python -u scripts/0.segment_nuclei.py \
                --patient "$patient" \
                --well_fov "$well_fov" \
                --clip_limit 0.03 \
                --twoD_method "$twoD_method" \
                --overwrite

            python scripts/1.segment_cells.py \
                --patient "$patient" \
                --well_fov "$well_fov" \
                --clip_limit 0.01 \
                --twoD_method "$twoD_method" \
                --overwrite
            python scripts/2.segment_organoids.py \
                --patient "$patient" \
                --well_fov "$well_fov" \
                --clip_limit 0.01 \
                --twoD_method "$twoD_method" \
                --overwrite
        else
            python -u scripts/0.segment_nuclei.py \
                --patient "$patient" \
                --well_fov "$well_fov" \
                --clip_limit 0.03 \
                --twoD_method "$twoD_method"

            python scripts/1.segment_cells.py \
                --patient "$patient" \
                --well_fov "$well_fov" \
                --clip_limit 0.01 \
                --twoD_method "$twoD_method"

            python scripts/2.segment_organoids.py \
                --patient "$patient" \
                --well_fov "$well_fov" \
                --clip_limit 0.01 \
                --twoD_method "$twoD_method"
        fi
    done
done < "$input_file"



conda deactivate

echo ""
echo "========================================="
echo "✓ Cell segmentation preprocessing completed successfully!"
