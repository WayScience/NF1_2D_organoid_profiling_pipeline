#!/bin/bash

module load anaconda
# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation

cd scripts/ || exit

patient=$1
z_stack_dir="../../data/$patient/zstack_images/"

mapfile -t well_fovs < <(ls -d "$z_stack_dir"/*)

total_dirs=$(echo "${well_fovs[@]}" | wc -w)
echo "Total directories: $total_dirs"
twoD_methods=( "zmax" "middle" )
# loop through all input directories
for well_fov in "${well_fovs[@]}"; do
    well_fov=${well_fov%*/}
    well_fov=$(basename "$well_fov")
    number_of_jobs=$(squeue -u $USER | wc -l)
    while [ $number_of_jobs -gt 990 ]; do
        sleep 1s
        number_of_jobs=$(squeue -u $USER | wc -l)
    done
    sbatch \
        --nodes=1 \
        --ntasks=1 \
        --account=amc-general \
        --parition=amilan \
        --qos=normal \
        --time=00:10:00 \
        --output="segmentation_child_${patient}_${well_fov}-%j.out" \
        HPC_child_segmentation.sh \
        "$patient" \
        "$well_fov"
done

cd ../ || exit

conda deactivate

echo "Cell segmentation preprocessing completed successfully."
