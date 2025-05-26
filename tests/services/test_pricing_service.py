import pytest

from app.services.pricing_service import PricingService, pricing_service as global_pricing_service
from app.core.config import settings
from app.schemas.enums import PricingTierEnum

# Test data directly from settings for consistency
TEST_PRICING_RATES = settings.PRICING_RATES

# Test using the globally instantiated pricing_service
# This ensures we are testing the same instance the app would use.
# Alternatively, one could instantiate PricingService directly with TEST_PRICING_RATES
# for more isolated unit tests if the global instance had complex dependencies (not the case here).

def test_calculate_shipment_cost_valid_tiers():
    """Test cost calculation for all valid pricing tiers."""
    for tier_name, tier_data in TEST_PRICING_RATES.items():
        expected_cost = float(tier_data["base_rate"])
        # Test with enum member
        calculated_cost_enum = global_pricing_service.calculate_shipment_cost(service_level=PricingTierEnum[tier_name].value)
        assert calculated_cost_enum == expected_cost
        
        # Test with string value (service should handle case-insensitivity or upper-casing)
        calculated_cost_str_lower = global_pricing_service.calculate_shipment_cost(service_level=tier_name.lower())
        assert calculated_cost_str_lower == expected_cost

        calculated_cost_str_upper = global_pricing_service.calculate_shipment_cost(service_level=tier_name.upper())
        assert calculated_cost_str_upper == expected_cost


def test_calculate_shipment_cost_invalid_tier():
    """Test cost calculation with an invalid service level."""
    invalid_service_level = "INVALID_TIER"
    with pytest.raises(ValueError) as excinfo:
        global_pricing_service.calculate_shipment_cost(service_level=invalid_service_level)
    assert f"Invalid service level: {invalid_service_level}" in str(excinfo.value)

def test_calculate_shipment_cost_with_package_details_placeholder():
    """
    Test cost calculation with package_details.
    Currently, package_details are not implemented in cost calculation,
    so this test ensures the function still works and returns the base rate.
    """
    standard_tier_name = PricingTierEnum.STANDARD.value
    expected_cost = float(TEST_PRICING_RATES[standard_tier_name]["base_rate"])
    
    calculated_cost = global_pricing_service.calculate_shipment_cost(
        service_level=standard_tier_name,
        package_details="Some details about the package"
    )
    assert calculated_cost == expected_cost

def test_get_available_pricing_tiers():
    """Test retrieval of available pricing tiers."""
    available_tiers = global_pricing_service.get_available_pricing_tiers()
    
    assert isinstance(available_tiers, list)
    assert len(available_tiers) == len(TEST_PRICING_RATES)
    
    for tier in available_tiers:
        assert "name" in tier
        assert "base_rate" in tier
        assert "description" in tier
        
        # Check if the data matches what's in settings
        assert tier["name"] in TEST_PRICING_RATES
        original_tier_data = TEST_PRICING_RATES[tier["name"]]
        assert tier["base_rate"] == original_tier_data.get("base_rate")
        assert tier["description"] == original_tier_data.get("description", "")

# Example of testing with a direct instance if needed for more isolation
def test_calculate_shipment_cost_isolated_instance():
    """Test cost calculation with an isolated PricingService instance."""
    isolated_rates = {
        "TEST_TIER": {"base_rate": 50.0, "description": "A special test tier."}
    }
    isolated_pricing_service = PricingService(pricing_rates=isolated_rates)
    
    # Test valid tier for isolated instance
    assert isolated_pricing_service.calculate_shipment_cost(service_level="TEST_TIER") == 50.0
    
    # Test invalid tier for isolated instance
    with pytest.raises(ValueError):
        isolated_pricing_service.calculate_shipment_cost(service_level="NON_EXISTENT_TIER")

    # Test get_available_pricing_tiers for isolated instance
    tiers = isolated_pricing_service.get_available_pricing_tiers()
    assert len(tiers) == 1
    assert tiers[0]["name"] == "TEST_TIER"
    assert tiers[0]["base_rate"] == 50.0
```
