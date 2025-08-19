#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --account=amc-general
#SBATCH --partition=amilan
#SBATCH --qos=normal
#SBATCH --time=00:30:00
#SBATCH --output="featurization_grandparent-%j.out"

jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb

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
        --partition=amilan \
        --qos=normal \
        --time=00:10:00 \
        --output="featurization_parent_${patient}-%j.out" \
        HPC_parent_featurization.sh \
        "$patient"
done

echo "Featurization completed successfully."
