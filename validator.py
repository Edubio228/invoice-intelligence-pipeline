from pydantic import BaseModel, Field
from typing import Optional, List


class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None


class Invoice(BaseModel):
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    line_items: Optional[List[LineItem]] = Field(default_factory=list)
    subtotal: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    source_file: Optional[str] = None


def validate_invoice(data: dict, source_file: str = "") -> Invoice:
    """Validate and coerce extracted invoice data into the Invoice model."""
    data["source_file"] = source_file
    return Invoice(**data)