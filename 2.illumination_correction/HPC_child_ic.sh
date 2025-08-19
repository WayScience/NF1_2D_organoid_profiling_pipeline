#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=amilan
#SBATCH --time=10:00
#SBATCH --qos=normal
#SBATCH --output=illumination_correction-%j.out

module load anaconda
# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash
# activate the CellProfiler environment
conda activate gff_cp_env

# convert Jupyter notebooks to scripts


cd scripts/ || exit 1

patient="$1"
python cp_illum_correction.py --patient "$patient"

conda deactivate

cd ../ || exit 1

echo "Illumination correction completed successfully."
