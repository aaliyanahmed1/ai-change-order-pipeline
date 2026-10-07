"""
confidence.py

This module computes the final confidence score for a ChangeOrder extraction.
Final confidence does NOT rely solely on the LLM's self-reported confidence.

The layered scoring formula:
1. Evidence Grounding: For each ExtractedField, if it has evidence, we fuzzy match 
   the evidence snippet against the normalized source document. If the match ratio 
   is < 85%, the evidence is considered fabricated, and the field's confidence is capped at 0.3.
2. Missing Fields Penalty: Certain key fields (e.g., total_amount, date) missing will trigger a review.
3. Overall Score Calculation: The overall score is the average of all individual field confidences
   after evidence capping.
4. Needs Review: If the overall score is below the provided threshold, needs_review is set to True.
"""

import re
from typing import List, Any
from rapidfuzz import fuzz
from schema import ChangeOrder, ExtractionResult, ExtractedField

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Lowercase and replace all whitespace sequences with a single space
    return re.sub(r'\s+', ' ', text.lower()).strip()

def check_evidence(evidence: str, source_text: str) -> bool:
    if not evidence:
        return False
    norm_evidence = normalize_text(evidence)
    norm_source = normalize_text(source_text)
    
    if not norm_evidence or not norm_source:
        return False
        
    if norm_evidence in norm_source:
        return True
        
    # Fuzzy match using partial_ratio since evidence is a snippet
    score = fuzz.partial_ratio(norm_evidence, norm_source)
    return score >= 85

def collect_fields(obj: Any) -> List[ExtractedField]:
    fields = []
    if isinstance(obj, ExtractedField):
        fields.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            fields.extend(collect_fields(item))
    elif hasattr(obj, '__dict__') and not isinstance(obj, ExtractedField): # BaseModel check
        for field_name, field_value in vars(obj).items():
            fields.extend(collect_fields(field_value))
    return fields

def compute_confidence(change_order: ChangeOrder, source_text: str, threshold: float = 0.8) -> ExtractionResult:
    review_reasons = []
    fields = collect_fields(change_order)
    
    total_confidence = 0.0
    valid_fields_count = 0
    
    for field in fields:
        # If a field has a value, check its evidence
        if field.value is not None:
            valid_fields_count += 1
            if field.evidence:
                if not check_evidence(field.evidence, source_text):
                    field.confidence = min(field.confidence, 0.3)
                    review_reasons.append(f"Evidence snippet '{field.evidence[:30]}...' not found in source text.")
            else:
                # Value provided but no evidence
                field.confidence = min(field.confidence, 0.5)
                review_reasons.append(f"Field extracted value '{field.value}' but provided no evidence.")
                
            total_confidence += field.confidence
        else:
            # Field value is None. Doesn't count towards average unless it's critical, handled below.
            pass
    
    overall_score = 1.0
    if valid_fields_count > 0:
        overall_score = total_confidence / valid_fields_count
        
    # Check critical missing fields (if missing, they don't even have value, so they didn't get added to valid_fields_count)
    if not hasattr(change_order, 'total_amount') or not getattr(change_order, 'total_amount') or change_order.total_amount.value is None:
        review_reasons.append("Missing critical field: total_amount")
        overall_score -= 0.2
        
    if not hasattr(change_order, 'date') or not getattr(change_order, 'date') or change_order.date.value is None:
        review_reasons.append("Missing critical field: date")
        overall_score -= 0.1
        
    # Cap score
    overall_score = max(0.0, min(1.0, overall_score))
    
    needs_review = bool(overall_score < threshold or len(review_reasons) > 0)
    
    return ExtractionResult(
        change_order=change_order,
        needs_review=needs_review,
        overall_score=overall_score,
        review_reasons=review_reasons
    )
