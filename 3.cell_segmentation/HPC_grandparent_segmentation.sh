#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --account=amc-general
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --time=00:10:00
#SBATCH --output="segmentation_grandparent-%j.out"


module load anaconda
# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the preprocessing environment
conda activate GFF_segmentation

patients_file="../data/patient_IDs.txt"
# read patient IDs from the file
mapfile -t patients < "$patients_file"


for patient in "${patients[@]}"; do
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
        --output="segmentation_parent_${patient}-%j.out" \
        HPC_parent_segmentation.sh \
        "$patient"
done


conda deactivate

echo "Cell segmentation preprocessing completed successfully."
