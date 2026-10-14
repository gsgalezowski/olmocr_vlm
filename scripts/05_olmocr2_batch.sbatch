#!/bin/bash -l
# Six-page, paired manual-reference benchmark. One model load, deterministic decode.
#SBATCH --job-name=olmocr2-batch6
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/olmocr2-batch-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/olmocr2-batch-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
test -f "$root/models/olmOCR-2-7B-1025-FP8/config.json"
singularity run "$SIF" python "$root/scripts/run_olmocr2_batch.py" \
  --model "$root/models/olmOCR-2-7B-1025-FP8" \
  --input-dir "$root/input/batch6" \
  --manifest "$root/input/batch_manifest.tsv" \
  --output-dir "$root/results/batch6" \
  --summary "$root/results/olmocr2_batch6_runtime.json"
