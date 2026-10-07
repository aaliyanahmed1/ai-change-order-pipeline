from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Generic, TypeVar
import datetime
from decimal import Decimal

T = TypeVar('T')

class ExtractedField(BaseModel, Generic[T]):
    value: Optional[T] = Field(default=None, description="The extracted value. Null if not found.")
    confidence: float = Field(ge=0.0, le=1.0, description="LLM self-reported confidence in this extraction (0.0 to 1.0).")
    evidence: Optional[str] = Field(default=None, description="The exact verbatim string snippet from the document that justifies this value. Null if not found.")

class Signature(BaseModel):
    name: ExtractedField[str] = Field(description="Name of the person signing")
    role: ExtractedField[str] = Field(description="Role or title of the person signing")
    date: ExtractedField[datetime.date] = Field(description="Date the signature was applied")
    signed: ExtractedField[bool] = Field(description="Whether the document is actually signed (true if signature mark exists)")

class LineItem(BaseModel):
    description: ExtractedField[str] = Field(description="Description of the work, material, or service")
    quantity: ExtractedField[Decimal] = Field(description="Quantity of items")
    unit_price: ExtractedField[Decimal] = Field(description="Price per unit")
    total_price: ExtractedField[Decimal] = Field(description="Total price for this line item")

class ChangeOrder(BaseModel):
    project_name: ExtractedField[str] = Field(description="Name of the construction project")
    change_order_number: ExtractedField[str] = Field(description="The specific Change Order ID or tracking number")
    date: ExtractedField[datetime.date] = Field(description="Date of the change order")
    owner_name: ExtractedField[str] = Field(description="Name of the project owner or client")
    contractor_name: ExtractedField[str] = Field(description="Name of the main contractor")
    vendor_name: ExtractedField[str] = Field(description="Name of the subcontractor or vendor issuing the change")
    description_of_change: ExtractedField[str] = Field(description="Overall description or reason for the change order")
    schedule_impact_days: ExtractedField[int] = Field(description="Number of days the schedule is impacted by this change (use 0 if no impact)")
    original_contract_sum: ExtractedField[Decimal] = Field(description="Original contract amount before this change")
    revised_contract_sum: ExtractedField[Decimal] = Field(description="Revised contract amount after this change")
    currency: ExtractedField[str] = Field(description="Currency code (e.g. USD, EUR)")
    total_amount: ExtractedField[Decimal] = Field(description="The grand total amount of the change order")
    line_items: List[LineItem] = Field(default_factory=list, description="List of individual line items representing the scope of work")
    signatures: List[Signature] = Field(default_factory=list, description="List of signatures present on the document")

    @model_validator(mode='after')
    def validate_math(self) -> 'ChangeOrder':
        # Sum validator
        if self.total_amount and self.total_amount.value is not None:
            sum_lines = sum((item.total_price.value for item in self.line_items if item.total_price and item.total_price.value is not None), Decimal('0.00'))
            if sum_lines > 0: # Only validate if we actually extracted line items with totals
                if abs(sum_lines - self.total_amount.value) > Decimal('0.02'):
                    raise ValueError(f"Sum of line items ({sum_lines}) does not match total_amount ({self.total_amount.value}).")

        # Line item quantity * unit_price == total_price
        for i, item in enumerate(self.line_items):
            if item.quantity and item.quantity.value is not None and item.unit_price and item.unit_price.value is not None and item.total_price and item.total_price.value is not None:
                calc_total = item.quantity.value * item.unit_price.value
                if abs(calc_total - item.total_price.value) > Decimal('0.02'):
                    raise ValueError(f"Line item {i} math mismatch: quantity ({item.quantity.value}) * unit_price ({item.unit_price.value}) != total_price ({item.total_price.value}).")
        
        return self

class ExtractionResult(BaseModel):
    """Wrapper that contains the LLM output and the pipeline-computed confidence."""
    change_order: ChangeOrder
    needs_review: bool = False
    overall_score: float = 1.0
    review_reasons: List[str] = Field(default_factory=list)
