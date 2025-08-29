#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --time=10:00
#SBATCH --qos=normal
#SBATCH --output=illumination_correction-%j.out


# convert Jupyter notebooks to scripts
jupyter nbconvert --to script --output-dir=scripts/ notebooks/*.ipynb


patient_array=( "NF0014_T1" "NF0016_T1" "NF0018_T6" "NF0021_T1" "NF0030_T1" "NF0040_T1" "SARCO219_T2" "SARCO361_T1" )

for patient in "${patient_array[@]}"; do
echo "Processing patient: $patient"
    # run Python script for performing illumination correction with CellProfiler
    sbatch HPC_child_ic.sh "$patient"
done


echo "Illumination correction completed successfully."
