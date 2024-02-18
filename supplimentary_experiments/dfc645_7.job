#!/bin/bash
#
#SBATCH --job-name=dfc645_7
#SBATCH --output=dfc645_7_job.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --partition=amd-hdr100
#SBATCH --time=08:00:00
#SBATCH --mem-per-cpu=4069

# load your Anaconda module here and activate your virtual environment (if needed)
set -e
source /home/ashovon/newaumri/matfiles/venv/bin/activate


# execute your python scripts (change it to whatever it needs to be for you).
python -u /home/ashovon/newaumri/matfiles/TemporalBrainPH/distance_calculation.py --data 645 --method bn --start 211 --end 240 --distance y --mds n

