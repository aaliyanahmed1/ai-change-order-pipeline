# Writeup

## 1. Approach
This prototype relies on the principle of "Schema as a Contract". Rather than writing complex Regex or layout heuristics, we define the exact output shape in `schema.py` using Pydantic (e.g., using strict `Decimal` for currency and `datetime.date` for dates). 

We wrap the OpenAI API using the `instructor` library. Instructor ensures that the LLM output conforms perfectly to our Pydantic schema. Crucially, I added `@model_validator` methods to the schema that mathematically verify the extraction (e.g., ensuring `sum(line_item.total) == grand_total`). If the math is wrong, Pydantic throws a validation error, which Instructor intercepts and feeds back to the LLM for a retry. 

For document ingestion, `PyMuPDF` extracts the raw text layer. If a PDF is detected to have an empty or nearly-empty text layer (like a scanned image), the pipeline automatically renders the pages as images and falls back to a vision-based extraction approach.

## 2. How Confidence is Computed
Relying purely on an LLM to self-report its confidence is insufficient because LLMs are highly prone to confidently hallucinating data. 

To solve this, confidence is computed through a layered scoring pipeline:
1. **Self-Report**: The LLM outputs its initial `confidence` and the verbatim string `evidence` it used from the text.
2. **Evidence Grounding**: The pipeline takes that `evidence` and performs a deterministic fuzzy match against the source document. If the LLM fabricated the evidence (fuzzy match < 85%), we heavily penalize the field's confidence, capping it at `0.3`, and log a review reason.
3. **Deterministic Checks**: We deduct points for missing critical fields (like `total_amount` or `date`).
4. **Final Threshold**: The overall score is averaged across fields. If it drops below `0.8` (configurable), `needs_review` is set to `True`.

## 3. Failure Modes
Based on the sample evaluations and architecture, here are the observed and handled failure modes:
* **Scanned Documents**: Handled via Vision fallback. If text is <50 chars/page, it converts the PDF to images for `gpt-4o`.
* **Math Mismatches**: Handled via Pydantic validators. If a document's table is confusing and the LLM extracts mismatched totals, the script retries automatically. If it still fails, it throws an error and requires review.
* **LLM Hallucinations**: Handled via Evidence Grounding. If the LLM makes up a value, it won't find the evidence in the source text, triggering the low-confidence penalty.
* **Extremely Long Documents**: Handled via truncation. If the text exceeds 50,000 characters, it truncates the document and forces a `needs_review` flag to ensure data wasn't missed.

**Not Yet Handled:**
* Hand-written annotations overlapping with printed text (Vision handles some of this, but it can be brittle).
* Documents exceeding the context window where truncating removes the actual change order table.

## 4. What I'd Do Next
1. **Layout-Aware Parsing**: Replace PyMuPDF text extraction with a layout-aware parser (like DocTR or LlamaParse) that reconstructs tables as Markdown before hitting the LLM. This significantly reduces tabular hallucinations.
2. **Chunking / Page Routing**: Instead of blind truncation, implement a fast classifier that finds the exact pages containing cost/scope tables and only sends those pages to the heavy extraction model.
3. **Calibration against a Labeled Set**: Build a labeled dataset of 500+ change orders to calibrate the fuzzy match thresholds and confidence penalties using a grid search, ensuring we hit optimal precision/recall.
4. **Human-Review UI**: Build a simple front-end where `needs_review=True` JSONs are presented side-by-side with the PDF, highlighting the bounding boxes of the `evidence` snippets for rapid human approval.
