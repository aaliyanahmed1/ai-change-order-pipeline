import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extractor import ChangeOrderExtractor

def run_evaluation():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY to run evaluate.py")
        sys.exit(1)
        
    extractor = ChangeOrderExtractor(api_key=api_key)
    samples = ["clean_co", "messy_co", "mismatch_co"]
    results = []
    
    os.makedirs("outputs", exist_ok=True)
    
    for s in samples:
        pdf_path = f"samples/{s}.pdf"
        expected_path = f"expected/{s}.json"
        
        with open(expected_path, "r") as f:
            expected = json.load(f)
            
        print(f"Evaluating {s}...")
        try:
            res = extractor.extract_from_file(pdf_path)
            co = res.change_order
            
            match_project = (co.project_name.value == expected["project_name"]) if co.project_name else False
            match_total = (str(co.total_amount.value) == expected["total_amount"]) if co.total_amount else False
            match_date = (str(co.date.value) == expected["date"]) if co.date else False
            match_lines = (len(co.line_items) == expected["line_items_count"]) if co.line_items else False
            
            results.append({
                "sample": s,
                "needs_review": res.needs_review,
                "overall_score": res.overall_score,
                "project_match": match_project,
                "total_match": match_total,
                "date_match": match_date,
                "lines_match": match_lines
            })
            
            if s == "clean_co":
                with open("outputs/example_output.json", "w") as f:
                    f.write(res.model_dump_json(indent=2))
                    
        except Exception as e:
            print(f"Failed {s}: {e}")
            results.append({"sample": s, "error": str(e)})
            
    print("\n| Sample | Needs Review | Score | Project | Total | Date | Lines |")
    print("|---|---|---|---|---|---|---|")
    for r in results:
        if "error" in r:
            print(f"| {r['sample']} | ERROR | {r['error']} |")
        else:
            print(f"| {r['sample']} | {r['needs_review']} | {r['overall_score']:.2f} | {r['project_match']} | {r['total_match']} | {r['date_match']} | {r['lines_match']} |")

if __name__ == "__main__":
    run_evaluation()
