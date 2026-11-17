# Datasets

This project does not ship with any historical-inscription dataset. Below
are the dataset slots the pipeline expects, and legitimate, publicly
documented dataset *types* you can source and drop in — no dataset name,
sample count, or license here is invented; verify current availability and
license terms directly from each source before use.

## 1. Script classification

**Expected structure:**
```
data/script_classification/
  train/<script_name>/*.jpg
  validation/<script_name>/*.jpg
  test/<script_name>/*.jpg
```
Classes should match `SUPPORTED_SCRIPTS` in `backend/app/ai/script_classifier.py`
(Tamil, Tamil-Brahmi, Vatteluttu, Grantha, Devanagari, Unknown).

**Where to look for source material:**
- Tamil Nadu Department of Archaeology / Epigraphy publications (digitized inscription photographs).
- University epigraphy/palaeography course archives (check licensing per item).
- Museum open-access collections that permit research reuse (verify each item's license individually — do not assume public-domain status).

Document every dataset you actually add here with:
```
Dataset name:
Source:
URL:
License:
Number of samples:
Language/script:
Purpose:
Preprocessing applied:
```

## 2. OCR

```
data/ocr/
  images/*.jpg
  transcriptions/*.txt   # one transcription file per image, same basename
```
Ground-truth transcriptions are required for CER/WER evaluation
(`scripts/evaluate_ocr.py`). If you don't have verified transcriptions yet,
use the pipeline in DEMO mode and treat outputs as unverified drafts.

## 3. Reconstruction (damage simulation)

```
data/reconstruction/
  original/*.txt      # clean, verified transcriptions
  damaged/*.txt        # same text with characters masked as [?] or _
```
`scripts/prepare_dataset.py` includes a masking utility to generate the
`damaged/` variants from `original/` automatically (random-character,
missing-character, and blur-simulated masking strategies).

## 4. Historical documents (RAG knowledge base)

```
data/historical_documents/
  *.pdf / *.txt / *.docx / *.md
```
Ingest with `scripts/ingest_documents.py`. Store bibliographic metadata
(title, author, year, publication, page, topic, region, period) alongside
each document — the RAG pipeline requires this to generate citations and
detect source conflicts.

---

**Rule enforced throughout this project:** no dataset is ever referred to
as if it exists in this repository unless it is physically present under
`data/`. Sample/test images used for development must be clearly labelled
as synthetic or placeholder, never presented as genuine archaeological
material.
