#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_cellprofiler

jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

input_file="../loadfiles/featurization_loadfile.txt"

cd scripts/ || exit
# set the counter to zero
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

    log_file="../logs/featurize_organoids_${patient}_${well_fov}.log"
    if [ -f "$log_file" ]; then
        rm "$log_file"
    fi
    mkdir -p "$(dirname "$log_file")"
    touch "$log_file"

    # call cellprofiler to run the analysis
    # this script runs all three max projection methods in parallel
    {
        python cp_analysis.py \
            --patient "$patient" \
            --well_fov "$well_fov"
    } &> "$log_file"

done < "$input_file"

cd ../ || exit

conda deactivate

echo "Cell segmentation preprocessing completed successfully."
