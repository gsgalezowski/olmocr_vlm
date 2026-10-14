#!/bin/bash -l
# Ten manually transcribed pages plus two held out pages: complete short HTR run.
#SBATCH --job-name=olmocr-lora-quick12
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/lora-quick12-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/lora-quick12-%j.err
set -euo pipefail
root=/project/project_465003327/olmocr_vlm
packages=/scratch/project_465003327/olmocr_vlm/train_python_compatible
module purge
module load Local-LAIF lumi-aif-singularity-bindings
sif=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$sif" env \
  HF_HOME=/scratch/project_465003327/olmocr_vlm/hf_cache \
  PYTHONPATH="$packages:$root/software/olmocr" \
  python -m olmocr.train.train --config "$root/configs/olmocr_lora_quick12.yaml"
