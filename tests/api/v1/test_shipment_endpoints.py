import pytest
import uuid
from httpx import AsyncClient
from fastapi import status

from app.schemas.shipment import ShipmentRead, ShipmentCreate
from app.schemas.address import AddressSchema
from app.schemas.enums import PricingTierEnum, ShipmentStatusEnum

# Helper to generate unique email for creating new users if needed
def unique_email_for_shipment_tests() -> str:
    return f"shipment_test_user_{uuid.uuid4().hex[:6]}@example.com"

# Default address for convenience
default_address_payload = {
    "address_line1": "123 Test St",
    "city": "Testville",
    "postal_code": "12345",
    "contact_name": "Test User",
    "contact_phone": "555-123-7890",
    "contact_email": "test.contact@example.com"
}

@pytest.mark.asyncio
async def test_create_shipment(authenticated_client: AsyncClient):
    """Test creating a new shipment with valid data."""
    shipment_data = {
        "pickup_address": default_address_payload,
        "delivery_address": {**default_address_payload, "address_line1": "456 Destination Ave"},
        "service_level": PricingTierEnum.STANDARD.value, # Ensure this is a string value
        "package_details": "1 box, 10kg, books"
    }
    
    response = await authenticated_client.post("/api/v1/shipments/", json=shipment_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    created_shipment = response.json()
    
    assert "id" in created_shipment
    assert "tracking_number" in created_shipment
    assert created_shipment["service_level"] == PricingTierEnum.STANDARD.value
    assert created_shipment["pickup_address"]["address_line1"] == "123 Test St"
    assert created_shipment["cost"] is not None # Cost should be calculated
    assert created_shipment["status"] == ShipmentStatusEnum.PENDING.value # Default status

@pytest.mark.asyncio
async def test_create_shipment_invalid_data(authenticated_client: AsyncClient):
    """Test creating a shipment with missing required fields (e.g., service_level)."""
    shipment_data_invalid = {
        "pickup_address": default_address_payload,
        "delivery_address": {**default_address_payload, "address_line1": "789 Bad Data Rd"},
        # "service_level": "STANDARD", # Missing service_level
        "package_details": "Invalid package"
    }
    response = await authenticated_client.post("/api/v1/shipments/", json=shipment_data_invalid)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_own_shipment_by_tracking_number(authenticated_client: AsyncClient):
    """Test retrieving a shipment owned by the authenticated user."""
    # 1. Create a shipment
    shipment_payload = {
        "pickup_address": default_address_payload,
        "delivery_address": {**default_address_payload, "address_line1": "111 My Street"},
        "service_level": PricingTierEnum.EXPRESS.value,
        "package_details": "Urgent documents"
    }
    create_response = await authenticated_client.post("/api/v1/shipments/", json=shipment_payload)
    assert create_response.status_code == status.HTTP_201_CREATED
    created_shipment_data = create_response.json()
    tracking_number = created_shipment_data["tracking_number"]

    # 2. Retrieve it
    get_response = await authenticated_client.get(f"/api/v1/shipments/{tracking_number}")
    assert get_response.status_code == status.HTTP_200_OK
    retrieved_shipment_data = get_response.json()
    assert retrieved_shipment_data["tracking_number"] == tracking_number
    assert retrieved_shipment_data["id"] == created_shipment_data["id"]
    assert retrieved_shipment_data["user_id"] == created_shipment_data["user_id"]


@pytest.mark.asyncio
async def test_get_other_user_shipment_by_tracking_number_forbidden(client: AsyncClient, authenticated_client: AsyncClient):
    """Test that a user cannot retrieve another user's shipment."""
    # 1. User A (authenticated_client) creates a shipment
    shipment_payload_user_a = {
        "pickup_address": default_address_payload,
        "delivery_address": {**default_address_payload, "address_line1": "User A's shipment"},
        "service_level": PricingTierEnum.STANDARD.value,
        "package_details": "User A package"
    }
    create_response_user_a = await authenticated_client.post("/api/v1/shipments/", json=shipment_payload_user_a)
    assert create_response_user_a.status_code == status.HTTP_201_CREATED
    tracking_number_user_a = create_response_user_a.json()["tracking_number"]

    # 2. User B (new authenticated client)
    email_user_b = unique_email_for_shipment_tests()
    password_user_b = "UserBPassword123"
    await client.post("/api/v1/auth/register", json={"email": email_user_b, "password": password_user_b})
    login_response_b = await client.post("/api/v1/auth/login", data={"username": email_user_b, "password": password_user_b})
    token_user_b = login_response_b.json()["access_token"]
    
    headers_user_b = {"Authorization": f"Bearer {token_user_b}"}

    # 3. User B tries to get User A's shipment
    response_user_b_get = await client.get(f"/api/v1/shipments/{tracking_number_user_a}", headers=headers_user_b)
    assert response_user_b_get.status_code == status.HTTP_404_NOT_FOUND # Or 403, current implementation returns 404 for this
    assert "Shipment not found or not authorized" in response_user_b_get.json()["detail"]


@pytest.mark.asyncio
async def test_list_own_shipments(authenticated_client: AsyncClient):
    """Test listing shipments for the authenticated user, including status filtering."""
    # Create a couple of shipments with different statuses
    payload1 = {
        "pickup_address": default_address_payload, "delivery_address": {**default_address_payload, "address_line1": "List St 1"},
        "service_level": PricingTierEnum.STANDARD.value, "package_details": "Std Pkg 1"
    }
    shipment1_resp = await authenticated_client.post("/api/v1/shipments/", json=payload1)
    assert shipment1_resp.status_code == status.HTTP_201_CREATED
    shipment1_id = shipment1_resp.json()["id"]

    payload2 = {
        "pickup_address": default_address_payload, "delivery_address": {**default_address_payload, "address_line1": "List St 2"},
        "service_level": PricingTierEnum.EXPRESS.value, "package_details": "Exp Pkg 2"
    }
    shipment2_resp = await authenticated_client.post("/api/v1/shipments/", json=payload2)
    assert shipment2_resp.status_code == status.HTTP_201_CREATED
    shipment2_id = shipment2_resp.json()["id"]

    # Update status of one shipment for filtering test
    await authenticated_client.patch(f"/api/v1/shipments/{shipment1_id}/status", json={"status": ShipmentStatusEnum.IN_TRANSIT.value})

    # List all shipments for the user
    list_response_all = await authenticated_client.get("/api/v1/shipments/")
    assert list_response_all.status_code == status.HTTP_200_OK
    shipments_all = list_response_all.json()
    assert len(shipments_all) >= 2 # Could be more if user ran other tests

    # List shipments filtered by status "pending"
    list_response_pending = await authenticated_client.get(f"/api/v1/shipments/?status={ShipmentStatusEnum.PENDING.value}")
    assert list_response_pending.status_code == status.HTTP_200_OK
    shipments_pending = list_response_pending.json()
    assert len(shipments_pending) >= 1
    for shipment in shipments_pending:
        if shipment["id"] == shipment2_id: # Only shipment2 should be pending among the ones created here
             assert shipment["status"] == ShipmentStatusEnum.PENDING.value

    # List shipments filtered by status "in_transit"
    list_response_in_transit = await authenticated_client.get(f"/api/v1/shipments/?status={ShipmentStatusEnum.IN_TRANSIT.value}")
    assert list_response_in_transit.status_code == status.HTTP_200_OK
    shipments_in_transit = list_response_in_transit.json()
    assert len(shipments_in_transit) >= 1
    for shipment in shipments_in_transit:
         if shipment["id"] == shipment1_id: # Only shipment1 should be in_transit
            assert shipment["status"] == ShipmentStatusEnum.IN_TRANSIT.value


@pytest.mark.asyncio
async def test_update_own_shipment_status(authenticated_client: AsyncClient):
    """Test updating the status of a shipment owned by the authenticated user."""
    # 1. Create a shipment
    payload = {
        "pickup_address": default_address_payload, "delivery_address": {**default_address_payload, "address_line1": "Status Update St"},
        "service_level": PricingTierEnum.ECONOMY.value, "package_details": "Status test pkg"
    }
    create_response = await authenticated_client.post("/api/v1/shipments/", json=payload)
    assert create_response.status_code == status.HTTP_201_CREATED
    shipment_id = create_response.json()["id"]

    # 2. Update its status
    new_status = ShipmentStatusEnum.DELIVERED.value
    update_response = await authenticated_client.patch(
        f"/api/v1/shipments/{shipment_id}/status", 
        json={"status": new_status}
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated_shipment = update_response.json()
    assert updated_shipment["status"] == new_status
    assert updated_shipment["id"] == shipment_id

@pytest.mark.asyncio
async def test_update_other_user_shipment_status_forbidden(client: AsyncClient, authenticated_client: AsyncClient):
    """Test that a user cannot update the status of another user's shipment."""
    # 1. User A (authenticated_client) creates a shipment
    payload_user_a = {
        "pickup_address": default_address_payload, "delivery_address": {**default_address_payload, "address_line1": "User A Status Update"},
        "service_level": PricingTierEnum.STANDARD.value, "package_details": "User A status package"
    }
    create_response_user_a = await authenticated_client.post("/api/v1/shipments/", json=payload_user_a)
    assert create_response_user_a.status_code == status.HTTP_201_CREATED
    shipment_id_user_a = create_response_user_a.json()["id"]

    # 2. User B (new authenticated client)
    email_user_b = unique_email_for_shipment_tests()
    password_user_b = "UserBPass456"
    await client.post("/api/v1/auth/register", json={"email": email_user_b, "password": password_user_b})
    login_response_b = await client.post("/api/v1/auth/login", data={"username": email_user_b, "password": password_user_b})
    token_user_b = login_response_b.json()["access_token"]
    headers_user_b = {"Authorization": f"Bearer {token_user_b}"}

    # 3. User B tries to update User A's shipment status
    response_user_b_update = await client.patch(
        f"/api/v1/shipments/{shipment_id_user_a}/status", 
        json={"status": ShipmentStatusEnum.CANCELLED.value},
        headers=headers_user_b
    )
    assert response_user_b_update.status_code == status.HTTP_403_FORBIDDEN
    assert "Not authorized to update this shipment's status" in response_user_b_update.json()["detail"]
```
