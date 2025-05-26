from typing import List

from fastapi import APIRouter, Depends

from app.schemas.pricing import PricingTierRead
from app.services.pricing_service import pricing_service # Import the instance

router = APIRouter(tags=["Pricing"])

@router.get(
    "/tiers", 
    response_model=List[PricingTierRead],
    summary="List available pricing tiers",
    description="Get a list of all available pricing tiers, including their names, base rates, and descriptions. This endpoint is public."
)
async def list_pricing_tiers():
    """
    Retrieves available pricing tiers from the pricing service.
    """
    tiers = pricing_service.get_available_pricing_tiers()
    return tiers
