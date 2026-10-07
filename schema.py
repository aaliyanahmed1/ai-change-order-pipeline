from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    description: str = Field(description="Description of the work, material, or service")
    quantity: Optional[float] = Field(default=None, description="Quantity of items, if applicable")
    unit_price: Optional[float] = Field(default=None, description="Price per unit, if applicable")
    total_price: Optional[float] = Field(default=None, description="Total price for this line item")

class ConfidenceScore(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0. Deduct points if the text is ambiguous, poorly formatted, or missing key tabular structures.")
    reasoning: str = Field(description="Brief reasoning for why this confidence score was given.")

class ChangeOrder(BaseModel):
    project_name: Optional[str] = Field(default=None, description="Name of the construction project")
    change_order_number: Optional[str] = Field(default=None, description="The specific Change Order ID or tracking number")
    date: Optional[str] = Field(default=None, description="Date of the change order in YYYY-MM-DD format")
    vendor_name: Optional[str] = Field(default=None, description="Name of the subcontractor or vendor issuing the change")
    total_amount: Optional[float] = Field(default=None, description="The grand total amount of the change order")
    line_items: List[LineItem] = Field(default_factory=list, description="List of individual line items representing the scope of work")
    signatures_present: bool = Field(description="Boolean indicating if the document contains signatures or is formally approved")
    confidence: ConfidenceScore = Field(description="Assessment of how confident the AI is in this extraction")
