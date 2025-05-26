from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.schemas.enums import PricingTierEnum

class PricingService:
    def __init__(self, pricing_rates: Dict[str, Dict[str, Any]]):
        self.pricing_rates = pricing_rates

    def calculate_shipment_cost(self, service_level: str, package_details: Optional[str] = None) -> float:
        """
        Calculates the shipment cost based on the service level.
        """
        effective_service_level = service_level.upper()
        
        if effective_service_level not in self.pricing_rates:
            raise ValueError(f"Invalid service level: {service_level}. Valid levels are {list(self.pricing_rates.keys())}")

        # For now, calculation is simple: just the base rate.
        # Future: package_details could be parsed for weight/dimensions to adjust cost.
        cost = self.pricing_rates[effective_service_level]["base_rate"]
        
        # Example placeholder for future logic based on package_details
        # if package_details:
        #     # Parse package_details (e.g., weight, dimensions)
        #     # Add additional charges based on these details
        #     pass
            
        return float(cost)

    def get_available_pricing_tiers(self) -> List[Dict[str, Any]]:
        """
        Returns a list of available pricing tiers with their details.
        """
        available_tiers = []
        for tier_name, tier_details in self.pricing_rates.items():
            available_tiers.append({
                "name": tier_name,
                "base_rate": tier_details.get("base_rate"),
                "description": tier_details.get("description", "")
            })
        return available_tiers

# Instantiate the service with settings
pricing_service = PricingService(pricing_rates=settings.PRICING_RATES)
