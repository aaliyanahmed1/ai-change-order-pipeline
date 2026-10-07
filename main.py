import os
import argparse
from extractor import ChangeOrderExtractor

def main():
    parser = argparse.ArgumentParser(description="AI Pipeline to extract structured JSON from Change Order PDFs.")
    parser.add_argument("file_path", help="Path to the PDF or text file to process")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Run: export OPENAI_API_KEY='your-key' (Linux/Mac) or set OPENAI_API_KEY='your-key' (Windows)")
        return

    # Initialize our extraction pipeline
    extractor = ChangeOrderExtractor(api_key=api_key)
    file_path = args.file_path
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return

    print(f"Reading document: {file_path}...")
    
    # Handle PDF vs Text
    if file_path.lower().endswith(".pdf"):
        text = extractor.extract_text_from_pdf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    print("Sending text to LLM for structured extraction (this may take a few seconds)...")
    try:
        result = extractor.process_document(text)
        
        # Serialize the Pydantic object to validated JSON
        json_output = result.model_dump_json(indent=2)
        print("\n--- EXTRACTED JSON ---")
        print(json_output)
        
        # Save output
        out_file = "extracted_data.json"
        with open(out_file, "w") as f:
            f.write(json_output)
        print(f"\n✅ Success! Saved extraction to {out_file}")
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")

if __name__ == "__main__":
    main()
