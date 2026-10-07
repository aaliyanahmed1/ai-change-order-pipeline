import instructor
from openai import OpenAI
import fitz  # PyMuPDF
from schema import ChangeOrder

class ChangeOrderExtractor:
    def __init__(self, api_key: str):
        # We patch the OpenAI client with Instructor.
        # Instructor guarantees that the output matches our Pydantic schema
        # and automatically handles retries if the LLM hallucinates bad JSON.
        self.client = instructor.from_openai(OpenAI(api_key=api_key))
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts raw text from a PDF file using PyMuPDF."""
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    # 'text' extraction gets the reading order
                    text += page.get_text("text") + "\n"
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF {pdf_path}: {e}")
        return text

    def process_document(self, text: str) -> ChangeOrder:
        """Uses LLM to extract structured data from raw text."""
        prompt = f"""
        You are an expert construction document analyst. 
        Your task is to extract change order details from the following unstructured text.
        
        INSTRUCTIONS:
        1. Look for standard change order fields: Project Name, Change Order Number, Total Amount, etc.
        2. Pay close attention to tabular data to extract individual line items.
        3. If a specific field is completely missing, return null/None. Do not guess.
        4. Provide a confidence score (0.0 to 1.0). If the text looks like a messy OCR scan where numbers might be wrong, lower the score.
        
        DOCUMENT TEXT:
        {text}
        """
        
        # This call enforces the ChangeOrder Pydantic schema
        change_order: ChangeOrder = self.client.chat.completions.create(
            model="gpt-4o", # You can swap this to gpt-4o-mini for cost efficiency
            response_model=ChangeOrder,
            messages=[{"role": "user", "content": prompt}],
            max_retries=3 # Automatically retry if validation fails
        )
        
        return change_order
