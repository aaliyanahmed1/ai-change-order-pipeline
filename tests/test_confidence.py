from schema import ExtractedField, ChangeOrder
from confidence import compute_confidence
from decimal import Decimal

def make_co(**kwargs):
    base = {
        "project_name": ExtractedField(value=None, confidence=1.0),
        "change_order_number": ExtractedField(value=None, confidence=1.0),
        "date": ExtractedField(value=None, confidence=1.0),
        "owner_name": ExtractedField(value=None, confidence=1.0),
        "contractor_name": ExtractedField(value=None, confidence=1.0),
        "vendor_name": ExtractedField(value=None, confidence=1.0),
        "description_of_change": ExtractedField(value=None, confidence=1.0),
        "schedule_impact_days": ExtractedField(value=None, confidence=1.0),
        "original_contract_sum": ExtractedField(value=None, confidence=1.0),
        "revised_contract_sum": ExtractedField(value=None, confidence=1.0),
        "currency": ExtractedField(value=None, confidence=1.0),
        "total_amount": ExtractedField(value=None, confidence=1.0)
    }
    base.update(kwargs)
    return ChangeOrder(**base)

def test_evidence_grounding_passes():
    co = make_co(project_name=ExtractedField(value="Alpha", confidence=0.9, evidence="Project Alpha"))
    res = compute_confidence(co, source_text="This is Project Alpha.", threshold=0.8)
    assert res.change_order.project_name.confidence == 0.9

def test_evidence_grounding_fails():
    co2 = make_co(project_name=ExtractedField(value="Beta", confidence=0.9, evidence="Project Beta"))
    res2 = compute_confidence(co2, source_text="This is Project Alpha.", threshold=0.8)
    assert res2.change_order.project_name.confidence <= 0.3
    assert any("not found" in r for r in res2.review_reasons)

def test_needs_review_threshold():
    co = make_co(project_name=ExtractedField(value="Alpha", confidence=0.9, evidence="Project Alpha"))
    res = compute_confidence(co, source_text="This is Project Alpha.", threshold=0.8)
    assert res.needs_review is True
    assert res.overall_score < 0.8
