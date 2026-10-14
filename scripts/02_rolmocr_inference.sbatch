#!/bin/bash -l
# Public 7B VLM inference on one image. It intentionally does not train.
#SBATCH --job-name=rolmocr-one-page
#SBATCH --account=project_465003327
#SBATCH --partition=small-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/rolmocr-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/rolmocr-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
scratch=/scratch/project_465003327/olmocr_vlm/${SLURM_JOB_ID}
mkdir -p "$scratch"
trap 'rm -rf "$scratch"' EXIT
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
test -f "$root/models/RolmOCR/config.json"

singularity run "$SIF" python "$root/scripts/run_rolmocr.py" \
  --model "$root/models/RolmOCR" \
  --image "$root/input/1.jpg" \
  --output "$root/results/rolmocr_page_1.txt" \
  | tee "$root/results/rolmocr_page_1_runtime.json"
