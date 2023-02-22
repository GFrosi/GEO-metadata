#!/bin/bash
#SBATCH --time=24:00:00  
#SBATCH --account=
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --mail-user=
#SBATCH --mail-type=FAIL,END
#SBATCH --job-name=geo-metadata-stand

module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt

echo "Starting"

#python GEO-metadata/main_stand.py -h

python GEO-metadata/standtarget/main_stand.py -f GEO_metadata_2023_91930.csv -d dict_regex_Histones_inputs.dict -o GEO_metadata_2023_91930_stand.csv

echo "Done"


