#!/bin/bash -l
# Custom direct-Transformers inference with the official olmOCR-2 FP8 model.
#SBATCH --job-name=olmocr2-one-page
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/olmocr2-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/olmocr2-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
test -f "$root/models/olmOCR-2-7B-1025-FP8/config.json"
singularity run "$SIF" python "$root/scripts/run_olmocr2.py" \
  --model "$root/models/olmOCR-2-7B-1025-FP8" \
  --image "$root/input/1.jpg" \
  --output "$root/results/olmocr2_page_1.txt" \
  | tee "$root/results/olmocr2_page_1_runtime.json"
