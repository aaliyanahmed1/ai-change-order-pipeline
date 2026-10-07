from schema import ExtractedField, ChangeOrder
from confidence import compute_confidence
from decimal import Decimal

def test_evidence_grounding_passes():
    co = ChangeOrder(
        project_name=ExtractedField(value="Alpha", confidence=0.9, evidence="Project Alpha")
    )
    res = compute_confidence(co, source_text="This is Project Alpha.", threshold=0.8)
    assert res.change_order.project_name.confidence == 0.9

def test_evidence_grounding_fails():
    co2 = ChangeOrder(
        project_name=ExtractedField(value="Beta", confidence=0.9, evidence="Project Beta")
    )
    res2 = compute_confidence(co2, source_text="This is Project Alpha.", threshold=0.8)
    assert res2.change_order.project_name.confidence <= 0.3
    assert any("not found" in r for r in res2.review_reasons)

def test_needs_review_threshold():
    # Missing critical fields drops score
    co = ChangeOrder(
        project_name=ExtractedField(value="Alpha", confidence=0.9, evidence="Project Alpha")
        # Missing total_amount and date
    )
    res = compute_confidence(co, source_text="This is Project Alpha.", threshold=0.8)
    assert res.needs_review is True
    assert res.overall_score < 0.8
