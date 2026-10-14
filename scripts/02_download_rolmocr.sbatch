#!/bin/bash -l
# Download public model weights once without occupying a GPU.
#SBATCH --job-name=rolmocr-download
#SBATCH --account=project_465003327
#SBATCH --partition=small
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:30:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/download-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/download-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
export HF_HOME="$root/hf_cache"
export HF_HUB_DISABLE_TELEMETRY=1

singularity run "$SIF" python - <<'PY'
from huggingface_hub import snapshot_download

path = snapshot_download(
    "reducto/RolmOCR",
    local_dir="/project/project_465003327/olmocr_vlm/models/RolmOCR",
)
print(f"MODEL_DOWNLOAD_OK={path}")
PY
du -sh "$root/models/RolmOCR"
find "$root/models/RolmOCR" -maxdepth 1 -type f -printf '%f %s bytes\n' | sort
