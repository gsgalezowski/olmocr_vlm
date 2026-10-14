#!/bin/bash -l
# Baseline for the same two validation pages used in the post-LoRA check.
#SBATCH --job-name=olmocr-base-heldout
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=00:15:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/base-heldout-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/base-heldout-%j.err
set -euo pipefail
root=/project/project_465003327/olmocr_vlm
scratch=/scratch/project_465003327/olmocr_vlm
packages=$scratch/train_python_compatible
module purge
module load Local-LAIF lumi-aif-singularity-bindings
sif=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$sif" env PYTHONPATH="$packages:$root/software/olmocr" \
  python "$root/scripts/run_lora_eval.py" \
  --model "$scratch/models/olmocr-2-7b-1025-bf16" \
  --input-dir "$scratch/data/quick_htr_data/eval" \
  --output-dir "$root/results/base_quick12_heldout" --page 19 --page 29
singularity run "$sif" python "$root/scripts/evaluate_lora_heldout.py" \
  --input-dir "$scratch/data/quick_htr_data/eval" \
  --prediction-dir "$root/results/base_quick12_heldout" \
  --out-dir "$root/results/base_quick12_heldout_evaluation"
