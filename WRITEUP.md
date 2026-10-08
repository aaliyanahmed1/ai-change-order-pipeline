# Writeup

## 1. What This Tool Does
This tool takes messy construction "Change Order" PDFs and uses AI to turn them into clean, structured data (JSON format). 

Instead of writing complicated rules to find data, we use a simple approach:
1. We define exactly what the data should look like using a "Schema" (like a blueprint for data).
2. We ask GPT-4o to read the PDF and fill out that blueprint.
3. Our code then does math checks. For example, it checks if all the line items actually add up to the total amount. If the AI made a math mistake, our code tells the AI to try again.
4. If a PDF is a scanned image, the tool is smart enough to take screenshots of the pages and use the AI's vision capabilities to read it.

## 2. How the "Confidence Score" Works
We can't just ask the AI "how confident are you?" because AI often lies and acts overly confident when it's wrong.

Instead, we built a smart scoring system:
1. When the AI pulls a number or name, we force it to also quote the exact text it saw in the PDF as "evidence".
2. Our code then searches the original PDF for that exact quote. 
3. If our code can't find that quote in the PDF, it means the AI made it up! We immediately drop the confidence score and flag the document for a human to review.
4. We also lower the score if important fields (like the Total Amount or Date) are missing entirely.

## 3. Where It Fails (And How We Fix It)
* **Scanned Images:** If the PDF has no text layer, we automatically switch to reading it as an image.
* **Bad Math:** If the AI reads the table wrong and the numbers don't add up, our code catches it before it becomes a problem and forces a retry.
* **Hallucinations (AI making things up):** Caught by our evidence checker.
* **Very Long Documents:** If the document is hundreds of pages long, we have to cut it off so it doesn't break the AI, which means we might miss data at the end. We flag these long documents for human review.

## 4. Next Steps
If I had more time, here is what I would add next:
1. **Highlighting UI:** A web dashboard that puts the PDF side-by-side with the extracted data, highlighting exactly where the AI found the numbers so a human can approve it in seconds.
2. **Table Parsing Tool:** Use a specialized tool to extract tables perfectly before giving them to the AI, which stops the AI from getting confused by weirdly shaped tables.
3. **Smart Page Finder:** Instead of feeding the whole PDF to the AI, build a quick filter that only feeds the pages containing cost numbers to the AI.
