#!/bin/bash
# activate the preprocessing environment
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

input_file="loadfiles/segmentation_loadfile.txt"


patient_well_fov_counter=0
# get the number of lines in the input file
total_lines=$(wc -l < "$input_file")

while IFS= read -r line; do
    ((patient_well_fov_counter++))

    # split the line into an array
    IFS=$'\t' read -r -a parts <<< "$line"

    patient="${parts[0]}"
    well_fov="${parts[1]}"
    twoD_method="${parts[2]}"

    echo "Submitted [$patient_well_fov_counter/$total_lines] $patient - $well_fov - $twoD_method"

    number_of_jobs=$(squeue -u $USER | wc -l)
    while [ $number_of_jobs -gt 990 ]; do
        sleep 1s
        number_of_jobs=$(squeue -u $USER | wc -l)
    done
    sbatch \
        --nodes=1 \
        --ntasks=1 \
        --account=amc-general \
        --partition=amilan \
        --qos=normal \
        --time=00:10:00 \
        --output="./logs/segmentation_child_${patient}_${well_fov}-%j.out" \
        HPC_child_segmentation.sh \
        "$patient" \
        "$well_fov" \
        "$twoD_method"

done < "$input_file"


echo "Cell segmentation preprocessing completed successfully."
