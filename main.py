import os
import sys
import argparse
import logging
from dotenv import load_dotenv

from extractor import ChangeOrderExtractor

def main():
    parser = argparse.ArgumentParser(description="Pipeline to extract structured JSON from Change Order documents.")
    parser.add_argument("file_path", help="Path to the PDF or text file to process")
    parser.add_argument("--out", help="Optional output JSON file path", default=None)
    parser.add_argument("--threshold", type=float, default=0.8, help="Confidence threshold below which review is needed (default: 0.8)")
    parser.add_argument("--model", type=str, default="gpt-4o", help="OpenAI model to use (default: gpt-4o)")
    args = parser.parse_args()

    # Basic logging setup
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    logger = logging.getLogger(__name__)

    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set. Please set it in .env or your shell.")
        sys.exit(1)

    extractor = ChangeOrderExtractor(api_key=api_key, model_name=args.model)
    
    if not os.path.exists(args.file_path):
        logger.error(f"File not found: {args.file_path}")
        sys.exit(1)

    logger.info(f"Processing document: {args.file_path}")
    
    try:
        result = extractor.extract_from_file(args.file_path, threshold=args.threshold)
        json_output = result.model_dump_json(indent=2)
        
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(json_output)
            logger.info(f"✅ Success! Saved extraction to {args.out}")
        else:
            print("\n--- EXTRACTED JSON ---")
            print(json_output)
            
        if result.needs_review:
            logger.warning("Document requires human review.")
            for reason in result.review_reasons:
                logger.warning(f" - {reason}")
                
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
