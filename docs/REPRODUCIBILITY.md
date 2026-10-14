# Reproducibility

## Checks available from this repository alone

Run `python tools/verify_package.py` with Python 3.10 or later. It verifies the SHA-256 inventory, parses Python sources without importing GPU dependencies and checks page counts, CER medians, character totals and pooled CER consistency from rounded per-page values. This is not a rerun of inference or a recalculation of edit distances from raw text.

The observed GPU preflight environment is in `provenance/environment_observed.json`. LoRA was exercised on one AMD MI250X GCD with BF16; training/inference used PyTorch, transformers, PEFT, PDF rendering and the upstream olmOCR training stack. No generic requirements.txt is provided because a complete verified portable environment was not recovered.

## Recompute metrics with the separate original data

Once the original `input/`, `data/` and prediction directories have been restored beside the scripts, run from the repository root:

```bash
python scripts/evaluate_batch.py --manifest scripts/batch_manifest.tsv --input-dir input/batch6 --prediction-dir results/batch6 --out-dir recomputed/olmocr_batch6
python scripts/evaluate_batch.py --manifest scripts/batch_manifest.tsv --input-dir input/batch6 --prediction-dir results/qwen_batch6 --out-dir recomputed/qwen_batch6
python scripts/evaluate_lora_heldout.py --input-dir data/quick_htr_data/eval --prediction-dir results/base_quick12_heldout --out-dir recomputed/base_heldout
python scripts/evaluate_lora_heldout.py --input-dir data/quick_htr_data/eval --prediction-dir results/lora_quick12_heldout --out-dir recomputed/lora_heldout
```

These commands intentionally write new results separately. The prediction prefix `olmocr2` is also used in the historical Qwen output filenames; it does not identify the actual model in that experiment.

## Inference/training

Consult the historical instructions and scripts. Adapt allocation, storage paths, containers and model locations before scheduling any jobs. Model weights and adapters are external to this upload. No GPU jobs were run as part of repository preparation. Setup scripts for all earlier failed dependency attempts are not present, so this is not a complete reconstruction of environment installation.
