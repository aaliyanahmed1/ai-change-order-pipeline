# Construction Change Order Extraction Pipeline

This repository contains a production-grade pipeline for extracting structured fields from messy, unstructured Change Order documents (PDFs and text) into validated JSON.

## Approach & Architecture

Extracting structured data from highly variable construction documents requires moving beyond simple Regex or template-based OCR. Our pipeline uses a combination of deterministic text extraction and an LLM-driven schema engine.

### Core Stack
*   **PyMuPDF (`fitz`)**: Used for fast, deterministic text layer extraction from born-digital PDFs.
*   **Pydantic**: Acts as the "contract" for our data. We define the exact schema we expect (`ChangeOrder`, `LineItem`, `ConfidenceScore`).
*   **Instructor**: Wraps the OpenAI API to enforce strict JSON schema compliance. If the LLM hallucinates invalid data (e.g., outputs a string instead of a float for `total_amount`), Instructor automatically catches the validation error, injects it back into the prompt, and retries the LLM call.
*   **OpenAI (`gpt-4o`)**: The reasoning engine that understands spatial context, tabular formats, and construction terminology to accurately map messy text to the strict schema.

### How Confidence Scores Work
We rely on **LLM Self-Reflection**. The schema includes a `ConfidenceScore` sub-model. The LLM is instructed to score its own extraction based on the legibility of the text, missing fields, or broken table layouts, and provide a textual `reasoning`. This allows downstream systems to route low-confidence extractions (e.g., < 80%) to a human-in-the-loop for manual review.

---

## Failure Modes & Edge Cases

When deploying this in a real construction environment, we must account for several failure modes:

1.  **Scanned/Image-based PDFs:**
    *   *Failure:* `PyMuPDF` extracts the text layer. If a PDF is a scanned image, the text layer is empty.
    *   *Solution:* We would need to integrate a Vision model (like `gpt-4o-vision` or AWS Textract) or an OCR engine (like Tesseract or DocTR) as a fallback layer prior to LLM processing.
2.  **Complex Nested Tables:**
    *   *Failure:* Standard PDF text extraction flattens tables. If a change order has highly complex nested tables or multi-line item descriptions without borders, the reading order might jumble numbers.
    *   *Solution:* Implementing a layout analysis tool (e.g., LlamaParse or Microsoft Document Intelligence) that parses bounding boxes and reconstructs markdown tables before feeding it to the LLM.
3.  **Token Limits & Context Window Exhaustion:**
    *   *Failure:* A 50-page change order with extensive architectural drawings attached might exceed token limits or cause the LLM to "forget" instructions in the middle (the "Lost in the Middle" phenomenon).
    *   *Solution:* Implement document chunking or use a routing agent that first identifies which pages actually contain the cost/scope data and drops the rest before extraction.
4.  **Math Hallucinations:**
    *   *Failure:* The LLM might extract line items perfectly but misread the `total_amount`.
    *   *Solution:* Add a `@model_validator` in the Pydantic schema that mathematically sums all `line_item.total_price` values and throws a validation error if it doesn't match the extracted `grand_total`. Instructor would then force the LLM to fix it.

## Setup & Usage

1. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

2. Export your OpenAI API Key:
```bash
export OPENAI_API_KEY="sk-your-api-key"
# On Windows: set OPENAI_API_KEY="sk-your-api-key"
```

3. Run the pipeline on a document:
```bash
python main.py path/to/your/change_order.pdf
```
