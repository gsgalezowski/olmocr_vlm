#!/bin/bash -l
# Same six pages and decode settings as OlmOCR; only the checkpoint changes.
#SBATCH --job-name=qwen25vl-batch6
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/qwen-batch-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/qwen-batch-%j.err
set -euo pipefail
root=/project/project_465003327/olmocr_vlm
model=/scratch/project_465003327/olmocr_vlm/models/qwen2.5-vl-7b-instruct
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$SIF" python "$root/scripts/run_olmocr2_batch.py" \
  --model "$model" --input-dir "$root/input/batch6" --manifest "$root/input/batch_manifest.tsv" \
  --output-dir "$root/results/qwen_batch6" --summary "$root/results/qwen_batch6_runtime.json"
