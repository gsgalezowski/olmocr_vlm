#!/bin/bash -l
# Evaluate the completed Qwen2.5-VL batch inside the same tested container.
#SBATCH --job-name=qwen25vl-eval6
#SBATCH --account=project_465003327
#SBATCH --partition=small
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/qwen-eval-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/qwen-eval-%j.err
set -euo pipefail
module purge
module load Local-LAIF lumi-aif-singularity-bindings
root=/project/project_465003327/olmocr_vlm
sif=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$sif" python "$root/scripts/evaluate_batch.py" \
  --manifest "$root/input/batch_manifest.tsv" \
  --input-dir "$root/input/batch6" \
  --prediction-dir "$root/results/qwen_batch6" \
  --out-dir "$root/results/qwen_batch6_evaluation"
