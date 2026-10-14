#!/bin/bash -l
# Download the parent VLM on scratch for a fair OlmOCR-vs-Qwen control.
#SBATCH --job-name=qwen25vl-download
#SBATCH --account=project_465003327
#SBATCH --partition=small
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/qwen-download-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/qwen-download-%j.err
set -euo pipefail
target=/scratch/project_465003327/olmocr_vlm/models/qwen2.5-vl-7b-instruct
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$SIF" python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen2.5-VL-7B-Instruct', local_dir='$target')"
du -sh "$target"
