from enum import Enum

class ShipmentStatusEnum(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED_DELIVERY = "failed_delivery"
    PICKUP_SCHEDULED = "pickup_scheduled"
    OUT_FOR_DELIVERY = "out_for_delivery"

class PricingTierEnum(str, Enum):
    EXPRESS = "EXPRESS"
    STANDARD = "STANDARD"
    ECONOMY = "ECONOMY"
