#!/bin/bash -l
# CPU-only import check for the exact official olmOCR source revision on LUMI.
#SBATCH --job-name=olmocr-train-import
#SBATCH --account=project_465003327
#SBATCH --partition=small
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/train-import-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/train-import-%j.err

set -euo pipefail
root=/project/project_465003327/olmocr_vlm
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif
singularity run "$SIF" env PYTHONPATH="$root/software/olmocr" python - <<'PY'
import importlib
import importlib.metadata as metadata

for package in ("torch", "transformers", "accelerate", "trl", "peft", "omegaconf", "einops", "augraphy"):
    module = importlib.import_module(package)
    try:
        version = metadata.version(package)
    except metadata.PackageNotFoundError:
        version = getattr(module, "__version__", "unknown")
    print(f"{package}={version}")
importlib.import_module("olmocr.train.train")
print("OLMOCR_TRAIN_IMPORT_OK")
PY
