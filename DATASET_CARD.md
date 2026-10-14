# Data card

## Title and creators

**olmocr_vlm: Pilot HTR Evaluation Data and Scripts from LUMI**

Author: Grzegorz Gałęzowski, Uniwersytet Kardynała Stefana Wyszyńskiego w Warszawie / Wydział Nauk Humanistycznych.
Experiment date: 2026-09-28. Package preparation: 2026-10-14.
Grant: PLL/2026/019908 (`pllhistpreproc`), LUMI test grant.

## What the dataset contains

Eight UTF-8 CSV/JSON evaluation files for four experiment conditions. The six-page conditions each report six rows. The BF16 base/LoRA conditions each report two rows. The 16 rows are condition-page observations, not 16 independent pages. There are eight unique page IDs across these evaluation tables.

Six-page page IDs: 2, 12, 33, 55, 71, 94. Two-page validation IDs: 19, 29.

## Schema

| Field | Meaning |
|---|---|
| `page_id` | Local source-page identifier; not an archive catalogue identifier |
| `ref_chars` | Reference length after original normalization |
| `pred_chars` | Prediction length after original normalization |
| `length_ratio` | Prediction/reference character-count ratio (six-page tables) |
| `cer` | Character Levenshtein edit count / reference character count |
| `wer` | Word Levenshtein edit count / reference word count (six-page tables) |
| `cer_pooled`, `wer_pooled` | Total edit count / total reference count, not an unweighted average |
| `cer_median`, `wer_median` | Median page-level ratio (six-page summaries) |

All rates are dimensionless, can exceed 1 and use a decimal point. Missing WER in the two-page experiment means it was not computed by that evaluator; it must not be reported as zero. Each JSON file has `pages` and pooled CER; six-page summaries have additional fields.

## Measurement protocol

The six-page evaluator applies Unicode NFC, converts CRLF/CR to LF and strips leading/trailing whitespace. Word tokens are whitespace-separated. The two-page evaluator applies NFC, converts CRLF to LF and strips outer whitespace. It reads the complete Markdown reference, including retained front matter. No extra removal of generated Markdown/front matter is applied. Consequently these measurements describe the original pipeline and are not clean-text-only benchmark scores.

## Source and exclusions

Original pages were manually transcribed in the local Google Awards source collection identified in the historical experiment documentation. Detailed archival provenance and redistribution rights are not established by this package. Raw images, reference text and generated page text are not included. The 98-page prepared corpus is also not included.

## Intended use

Technical inspection of pilot outputs, evaluation-method review and reporting the work performed on LUMI. Not intended for claims of manuscript-disjoint generalization or a final model ranking. Two validation pages do not establish statistical reliability.

## Access and license

Zenodo DOI `10.5281/zenodo.23362662` is reserved for version 1.0.0 and is registered when the record is published. Evaluation data and research documentation are licensed under CC BY 4.0; code and training configurations are licensed under MIT. See RIGHTS.md and docs/DATA_AVAILABILITY.md. The deposit metadata describes this numerical evaluation dataset and does not claim distribution of the 98-page corpus.
