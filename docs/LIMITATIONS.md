# Limitations

- This is a technical pilot, not a representative benchmark.
- Inference used a custom direct-Transformers path rather than the complete recommended olmOCR toolkit pipeline with its rendering, rotation and retry logic. The archived scores therefore characterize this experimental setup, not the full product.
- The six-page comparison and the two-page base/LoRA comparison are different experiments. Their scores must not be pooled into one model ranking.
- Pages 19 and 29 were excluded from gradient training but were used for validation. They are not a final untouched test set.
- Document/hand-disjoint sampling was not established.
- Generated structural markup and reference front matter affect the archived metrics. Changing normalization requires new metrics and a distinct protocol version.
- Large insertion errors cause CER/WER above 1; they should not be capped at 100%.
- Reduced over-generation on two pages does not establish general model quality.
- Original Slurm scripts contain site-specific paths. Container names ending in `latest` are not immutable environment identifiers.
- Model revisions and every training dependency are not fully pinned. The recorded environment is evidence of the run, not a lockfile.
- Raw inputs, predictions and adapters are withheld from this upload; numerical metric consistency alone is not end-to-end reproduction.
- Historical documents are preserved for provenance. This README/data card takes precedence for the scope of this distributed package.
