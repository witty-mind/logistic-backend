from typing import Optional
from pydantic import BaseModel, Field

class PricingTierRead(BaseModel):
    name: str = Field(..., description="Name of the pricing tier.", example="EXPRESS")
    base_rate: float = Field(..., description="Base rate for this pricing tier.", example=20.0)
    description: Optional[str] = Field(None, description="Description of the pricing tier.", example="Fastest delivery option.")

    class Config:
        orm_mode = True 
        schema_extra = {
            "description": "Schema representing a pricing tier with its rate and description."
        }
