import pytest
import datetime
from decimal import Decimal
from pydantic import ValidationError
from schema import ChangeOrder, ExtractedField, LineItem

def test_sum_validator_passes():
    co = ChangeOrder(
        project_name=ExtractedField(value="Test"),
        total_amount=ExtractedField(value=Decimal('15.00'), confidence=1.0),
        line_items=[
            LineItem(
                description=ExtractedField(value="Item 1"),
                quantity=ExtractedField(value=Decimal('1.0')),
                unit_price=ExtractedField(value=Decimal('10.00')),
                total_price=ExtractedField(value=Decimal('10.00'))
            ),
            LineItem(
                description=ExtractedField(value="Item 2"),
                quantity=ExtractedField(value=Decimal('1.0')),
                unit_price=ExtractedField(value=Decimal('5.00')),
                total_price=ExtractedField(value=Decimal('5.00'))
            )
        ]
    )
    assert co.total_amount.value == Decimal('15.00')

def test_sum_validator_fails():
    with pytest.raises(ValidationError):
        ChangeOrder(
            project_name=ExtractedField(value="Test"),
            total_amount=ExtractedField(value=Decimal('20.00'), confidence=1.0),
            line_items=[
                LineItem(
                    description=ExtractedField(value="Item 1"),
                    quantity=ExtractedField(value=Decimal('1.0')),
                    unit_price=ExtractedField(value=Decimal('10.00')),
                    total_price=ExtractedField(value=Decimal('10.00'))
                )
            ]
        )

def test_date_parsing_passes():
    co = ChangeOrder(date=ExtractedField(value=datetime.date(2026, 5, 10)))
    assert co.date.value.year == 2026

def test_invalid_date_fails():
    # Pydantic fails validation if date is a bad string
    with pytest.raises(ValidationError):
        ChangeOrder(date=ExtractedField(value="not-a-date"))
