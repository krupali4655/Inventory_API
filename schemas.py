from pydantic import BaseModel, Field
from typing import Optional

# --- CATEGORY SCHEMAS ---
class CategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Category Name")
    description: Optional[str] = Field(None, description="Description of category")

# --- INVENTORY SCHEMAS ---
class ItemCreateSchema(BaseModel):
    product_name: str = Field(..., min_length=1)
    category_id: int = Field(..., gt=0, description="Valid Category ID")
    quantity: int = Field(..., ge=0, description="Stock Quantity")
    price: float = Field(..., gt=0, description="Price must be positive")

class ItemUpdateSchema(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, gt=0)