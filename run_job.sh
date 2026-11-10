#!/bin/bash
#SBATCH --job-name=mc-pi
#SBATCH --account=compfor203f26s001_class
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=512M
#SBATCH --time=00:20:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

cd "$SLURM_SUBMIT_DIR"
mkdir -p results
echo "$SLURM_JOB_ID" > results/job_id.txt

module load mamba
eval "$(conda shell.bash hook)"
conda activate monte-carlo-pi

echo "Job ID: $SLURM_JOB_ID"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Python: $(which python)"
python --version

python monte_carlo_pi.py
