## Analysis on Cheaha
- Open the local directory in terminal.
- Copy all the files from local directory to Cheaha:
```
scp -r . ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/
```
- Open an SSH connection to Cheaha:
```
ssh ashovon@cheaha.rc.uab.edu
```
- Change directory to the desired directory:
```
cd newaumri/matfiles/analysis/
```
- Create a virtual environment to one directory up. 
So, we can pull the current directory to local machine again without the venv files.
```
python3 -m venv ../venv
```
- Activate the environment:
```
source ../venv/bin/activate
```
- Upgrade pip:
```
pip install --upgrade pip
```
- Install the requirements:
```
pip install -r requirements.txt
```
- Upload a file from local machine to Cheaha:
```
scp README.md ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/
scp run_bg.sh ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/
scp distance_calculation.py ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/
scp cluster_calculation.py ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/
```
- Upload all files from a local directory to Cheaha recursively:
```
scp -r . ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/dfc_1400_subjects_distance_matrix/
scp -r . ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/dfc_1400_subjects_mds/
scp -r . ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/dfc_2500_subjects_mds/
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/analysis/clusters_kmeans/ . 
```
- Download single file from Cheaha to local machine:
```
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_645_subjects_mds/subject_1.json .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_645_down_subjects_mds_ws/subject_1.json .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_2500_subjects_mds/subject_1.json .

scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/TemporalBrainPH/clusters_bn.csv .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_645_normal_nonan/normalize_dfc_645_subject_1_time_1.txt .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_645_normal_nonan/normalize_dfc_645_subject_2_time_4.txt .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/normalize_645.m .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/normalize_1400.m .
scp ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/normalize_2500.m .
```
- Download all files from a Cheaha directory to local machine:
```
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/clusters_kmeans_bn/ .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/clusters_kmeans/ .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/clusters_kmeans_non_tda/ .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_2500_subjects_mds_ws/ .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_1400_subjects_mds_ws/ .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_645_subjects_mds_ws/ .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_2500_normal/ .
```
- Download all files from a Cheaha directory to local machine which has a specific pattern:
```shell
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/dfc_645_normal/normalize_dfc_645_subject_1_time_\*.txt .
scp -r ashovon@cheaha.rc.uab.edu:/home/ashovon/newaumri/matfiles/TemporalBrainPH/dfc\*.job .
```
- Create a batch job:
```
#!/bin/bash
#
#SBATCH --job-name=dfc645
#SBATCH --output=dfc645_job.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --partition=amd-hdr100
#SBATCH --time=10:00:00
#SBATCH --mem-per-cpu=4069

# load your Anaconda module here and activate your virtual environment (if needed)
set -e
source /home/ashovon/newaumri/matfiles/venv/bin/activate


# execute your python scripts (change it to whatever it needs to be for you).
python -u /home/ashovon/newaumri/matfiles/TemporalBrainPH/distance_calculation.py
```
- Run the Job in Cheaha:
```
sbatch dfc645.job
sbatch dfc1400.job
sbatch dfc2500.job
sbatch dfc645_nontda.job
sbatch dfc1400_nontda.job
sbatch dfc2500_nontda.job
sbatch clusteringresult.job
```
- To kill a Slurm job
```
scancel <jobid>
```
You can find your jobid with the following command:
``` 
squeue -u $USER
```
- See the users in a partition:
```
squeue -p amd-hdr100
```
- See the command history:
```shell
history | cut -c 8-
```
- See last 5 lines for a pattern of files:
```shell
tail -n 5 dfc645_*_job.out
tail -n 2 dfc645_*.job
```
- Check details of a job, (13626634 is the job id):
```
squeue -j 13626634 -o "%all"
```
- Check job history for a user within a specific start and end time:
```shell
sacct --accounts ashovon  --format=jobname,elapsed,ncpus,state --starttime 2023-02-20 --endtime 2023-02-22
```
- See the running scripts for the user:
```
ps aux | grep ashovon
```
- Get a medium instance:
```
srun --ntasks=1 --cpus-per-task=6 --mem-per-cpu=8192 --time=50:00:00 --partition=medium --job-name=fmri --pty /bin/bash
srun --ntasks=4 --cpus-per-task=6 --mem-per-cpu=8192 --time=50:00:00 --partition=medium --job-name=fmri_1400 --pty /bin/bash
```
