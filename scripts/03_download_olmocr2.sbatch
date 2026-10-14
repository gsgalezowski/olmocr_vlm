#!/bin/bash -l
# Download the official Apache-2.0 FP8 olmOCR-2 model without a GPU.
#SBATCH --job-name=olmocr2-download
#SBATCH --account=project_465003327
#SBATCH --partition=small
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:30:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/olmocr2-download-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/olmocr2-download-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
export HF_HOME="$root/hf_cache"
export HF_HUB_DISABLE_TELEMETRY=1
singularity run "$SIF" python - <<'PY'
from huggingface_hub import snapshot_download
path = snapshot_download("allenai/olmOCR-2-7B-1025-FP8", local_dir="/project/project_465003327/olmocr_vlm/models/olmOCR-2-7B-1025-FP8")
print(f"MODEL_DOWNLOAD_OK={path}")
PY
du -sh "$root/models/olmOCR-2-7B-1025-FP8"
