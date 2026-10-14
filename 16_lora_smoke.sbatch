#!/bin/bash -l
# Two training examples plus one validation page: validates the full LoRA path.
#SBATCH --job-name=olmocr-lora-smoke
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/lora-smoke-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/lora-smoke-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
packages=/scratch/project_465003327/olmocr_vlm/train_python_compatible
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$SIF" env \
  HF_HOME=/scratch/project_465003327/olmocr_vlm/hf_cache \
  PYTHONPATH="$packages:$root/software/olmocr" \
  python -m olmocr.train.train --config "$root/configs/olmocr_lora_smoke.yaml"
