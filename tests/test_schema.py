import pytest
import datetime
from decimal import Decimal
from pydantic import ValidationError
from schema import ChangeOrder, ExtractedField, LineItem

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

def test_sum_validator_passes():
    co = make_co(
        project_name=ExtractedField(value="Test", confidence=1.0),
        total_amount=ExtractedField(value=Decimal('15.00'), confidence=1.0),
        line_items=[
            LineItem(
                description=ExtractedField(value="Item 1", confidence=1.0),
                quantity=ExtractedField(value=Decimal('1.0'), confidence=1.0),
                unit_price=ExtractedField(value=Decimal('10.00'), confidence=1.0),
                total_price=ExtractedField(value=Decimal('10.00'), confidence=1.0)
            ),
            LineItem(
                description=ExtractedField(value="Item 2", confidence=1.0),
                quantity=ExtractedField(value=Decimal('1.0'), confidence=1.0),
                unit_price=ExtractedField(value=Decimal('5.00'), confidence=1.0),
                total_price=ExtractedField(value=Decimal('5.00'), confidence=1.0)
            )
        ]
    )
    assert co.total_amount.value == Decimal('15.00')

def test_sum_validator_fails():
    with pytest.raises(ValidationError):
        make_co(
            project_name=ExtractedField(value="Test", confidence=1.0),
            total_amount=ExtractedField(value=Decimal('20.00'), confidence=1.0),
            line_items=[
                LineItem(
                    description=ExtractedField(value="Item 1", confidence=1.0),
                    quantity=ExtractedField(value=Decimal('1.0'), confidence=1.0),
                    unit_price=ExtractedField(value=Decimal('10.00'), confidence=1.0),
                    total_price=ExtractedField(value=Decimal('10.00'), confidence=1.0)
                )
            ]
        )

def test_date_parsing_passes():
    co = make_co(date=ExtractedField(value=datetime.date(2026, 5, 10), confidence=1.0))
    assert co.date.value.year == 2026

def test_invalid_date_fails():
    with pytest.raises(ValidationError):
        make_co(date=ExtractedField(value="not-a-date", confidence=1.0))
