#!/bin/bash -l
# CPU-only, dependency-triggered evaluation of the OlmOCR paired benchmark.
#SBATCH --job-name=olmocr2-eval6
#SBATCH --account=project_465003327
#SBATCH --partition=small
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/olmocr2-eval-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/olmocr2-eval-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
module load cray-python/3.11.7
python "$root/scripts/evaluate_batch.py" \
  --manifest "$root/input/batch_manifest.tsv" \
  --input-dir "$root/input/batch6" \
  --prediction-dir "$root/results/batch6" \
  --out-dir "$root/results/batch6_evaluation"
