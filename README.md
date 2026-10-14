# olmocr_vlm

**Pilot HTR experiments with olmOCR on LUMI: evaluation data, scripts and research documentation.**

This repository documents a technical pilot performed on 28 September 2026. It includes page-level CER/WER measurements, aggregate results, inference/evaluation code and original Slurm/LoRA configurations. It is not a full HTR benchmark or a complete training corpus.

The archived inference measurements were produced with a custom direct-Transformers path. They do not evaluate the complete recommended olmOCR toolkit pipeline, including its rendering, rotation and retry logic. Results therefore describe this experimental configuration and dataset only.

**Author:** Grzegorz Gałęzowski  
**Affiliation:** Uniwersytet Kardynała Stefana Wyszyńskiego w Warszawie / Wydział Nauk Humanistycznych  
**Grant:** PLL/2026/019908 · `pllhistpreproc` · LUMI test grant  
**Research team:** `plggarchiai`  
**Grant applicant:** Artur Górak  
**LUMI allocation:** `project_465003327`

## Research scope

- Technical validation of OCR/VLM execution on an AMD Instinct MI250X GCD.
- Comparison of olmOCR-2 and Qwen2.5-VL on the same six manually transcribed pages.
- A one-page RolmOCR feasibility test (reported in the historical documentation).
- LoRA smoke training (2 training pages + 1 validation page).
- Short LoRA training (10 training pages + 2 validation pages), followed by evaluation on the same two validation pages.

The two validation pages were not training examples, but they were used for validation during training. They are **not an independent final test set**. The broader 98-page pilot split described in historical documents is not included in this repository.

## Recorded results

| Experiment | Pages | Pooled CER | Pooled WER |
|---|---:|---:|---:|
| olmOCR-2 FP8, six-page inference | 6 | 1.698142 | 1.716266 |
| Qwen2.5-VL, same six pages | 6 | 1.970521 | 2.601664 |
| olmOCR-2 BF16 base, validation pages 19 and 29 | 2 | 5.264778 | Not computed |
| olmOCR-2 BF16 + LoRA, same validation pages | 2 | 0.964827 | Not computed |

CER/WER are ratios, not percentages; insertion errors can make them exceed 1. These are the archived measurements under the original normalization protocol. They do not establish general superiority, production readiness or statistically reliable improvement. See [the data card](DATASET_CARD.md) and [limitations](docs/LIMITATIONS.md).

Within this limited setup, olmOCR 2 produced a lower pooled CER than the Qwen2.5-VL control on the same six pages. The upstream olmOCR training stack also ran end-to-end on LUMI-G, and the short LoRA pilot reduced over-generation on the two validation pages. These are feasibility observations rather than benchmark claims.

## Upstream project and citation

olmOCR is developed and maintained by the AllenNLP team at the Allen Institute for AI (AI2). This repository is an independent downstream pilot and is not affiliated with or endorsed by AI2.

- Project: [allenai/olmocr](https://github.com/allenai/olmocr)
- Model: [allenai/olmOCR-2-7B-1025](https://huggingface.co/allenai/olmOCR-2-7B-1025)
- Paper: Jake Poznanski, Luca Soldaini and Kyle Lo, *olmOCR 2: Unit Test Rewards for Document OCR*, arXiv:2510.19817 (2025), https://arxiv.org/abs/2510.19817

## Files

| Location | Contents |
|---|---|
| `results/*_evaluation/` | Numerical page-level and aggregate evaluation data |
| `scripts/` | Inference and metric calculation code; original Slurm scripts |
| `configs/` | Original LoRA training configurations |
| Root `*.sbatch` | Later experimental jobs |
| `docs/REPRODUCIBILITY.md` | Environment and reproduction boundaries |
| `docs/PLGRID_REPORTING.md` | Grant identifiers, reporting guidance and draft factual summary |
| `provenance/` | Source checksums, provenance and file inclusion decisions |
| `CITATION.cff` | Author and citation metadata; no DOI has yet been assigned |

Historical Polish documents at the repository root describe the larger local experiment archive. Their references to input scans, model outputs, logs or adapters **do not mean those files are distributed here**. Some are dated working recommendations, not validated final scientific conclusions.

## Data and model availability

This upload deliberately contains numerical evaluation data, code and documentation. Input scans, reference transcriptions, generated page texts, LoRA weights, optimizer states, full logs and the original archive remain in the separate local experiment copy. Public redistribution of those materials has not been confirmed. The underlying models must be obtained from their original providers under their terms. See [the availability statement](docs/DATA_AVAILABILITY.md).

## Reproducibility

The evaluation scripts use Python's standard library. Inference/training requires the LUMI GPU environment and external dependencies. Original job files contain allocation-specific paths and are archival examples, not portable one-click jobs. Numerical consistency and file integrity can be checked with:

```bash
python tools/verify_package.py
```

Raw-prediction metric reproduction requires the separately retained inputs and predictions. See [reproduction instructions](docs/REPRODUCIBILITY.md).

## Acknowledgements

The pilot used LUMI through Poland's PLGrid infrastructure under grant **PLL/2026/019908** (`pllhistpreproc`). We acknowledge PLGrid's allocation and support, the EuroHPC Joint Undertaking as owner of LUMI, and CSC (Finland) and the LUMI consortium as hosts.

See [acknowledgements](ACKNOWLEDGEMENTS.md) for identifiers and official guidance.

## Publication status and reuse

This is a repository prepared for deposit, not evidence that a DOI or a peer-reviewed publication exists. A DOI must be added only after the corresponding repository record is published. Code and training configurations use [MIT](LICENSE); evaluation data and research documentation use [CC BY 4.0](LICENSE-DATA.md). See [RIGHTS.md](RIGHTS.md) for the file-level scope. The repository does not replace the grant report or establish its acceptance by PLGrid.
