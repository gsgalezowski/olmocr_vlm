#!/bin/bash -l
# Short, auditable ROCm framework check. It does not download or train a model.
#SBATCH --job-name=olmocr-rocm-check
#SBATCH --account=project_465003327
#SBATCH --partition=dev-g
#SBATCH --gpus=1
#SBATCH --cpus-per-task=7
#SBATCH --mem=64G
#SBATCH --time=00:10:00
#SBATCH --output=/project/project_465003327/olmocr_vlm/logs/framework-%j.out
#SBATCH --error=/project/project_465003327/olmocr_vlm/logs/framework-%j.err

set -euo pipefail
module purge
module load Local-LAIF lumi-aif-singularity-bindings
export SIF=/appl/local/laifs/containers/lumi-multitorch-latest.sif

singularity run "$SIF" python - <<'PY'
import importlib.metadata as metadata
import importlib.util
import json
import torch

packages = {}
for package in ("torch", "transformers", "huggingface-hub", "vllm", "flash-attn"):
    try:
        packages[package] = metadata.version(package)
    except metadata.PackageNotFoundError:
        packages[package] = None

assert torch.cuda.is_available(), "ROCm PyTorch did not expose the allocated GCD"
device = torch.device("cuda:0")
x = torch.randn((1024, 1024), device=device, dtype=torch.bfloat16)
y = x @ x
torch.cuda.synchronize()
print(json.dumps({
    "torch": torch.__version__,
    "hip": torch.version.hip,
    "device": torch.cuda.get_device_name(device),
    "visible_devices": torch.cuda.device_count(),
    "packages": packages,
    "matrix_checksum": float(y[0, :16].float().sum().item()),
}, indent=2))
PY
