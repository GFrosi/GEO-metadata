#!/bin/bash
#SBATCH --time=6:00:00  
#SBATCH --account=
#SBATCH --cpus-per-task=4
#SBATCH --mem=10G
#SBATCH --mail-user=
#SBATCH --mail-type=FAIL,END
#SBATCH --job-name=geo-metadata

module load python/3.6
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt

echo "Starting"

#python GEO-metadata/main.py -h

python GEO-metadata/main.py -f XML_Parser/GEO_2023_filtered_Hs_ChIP_nodup.csv -s XML_Parser/gsm_srx_srr_ids_all.csv -d dict_regex_Histones_inputs.dict

echo "Done"


