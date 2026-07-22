import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.mark.asyncio
async def test_api_initialize_station():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/stations/initialize", json={
            "name": "API Test Station Unique 1",
            "address": "100 API St",
            "seed_slots": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "API Test Station Unique 1"
        
        # Verify slots get endpoint
        slots_response = await client.get(f"/api/stations/{data['id']}/slots")
        assert slots_response.status_code == 200
        slots = slots_response.json()
        assert len(slots) == 6

@pytest.mark.asyncio
async def test_api_full_deposit_confirm_and_retrieval_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Initialize station
        init_res = await client.post("/api/stations/initialize", json={
            "name": "Flow Station Unique 2",
            "address": "200 Flow Ave",
            "seed_slots": True
        })
        assert init_res.status_code == 200
        station_id = init_res.json()["id"]
        
        # 2. Deposit courier package
        deposit_res = await client.post("/api/allocations/deposit-courier", json={
            "station_id": station_id,
            "package_identifier": "API-PKG-01",
            "courier_name": "Shopee Xpress",
            "courier_code": "SPX-99",
            "recipient_phone": "+60123456789",
            "package_size": "SMALL"
        })
        assert deposit_res.status_code == 200
        dep_data = deposit_res.json()
        allocation_id = dep_data["allocation"]["id"]
        raw_code = dep_data["raw_pickup_code"]
        slot_code = dep_data["unlocked_slot"]["slot_code"]
        
        # 3. Confirm deposit (close door & dispatch SMS)
        confirm_res = await client.post("/api/allocations/deposit-confirm", json={
            "allocation_id": allocation_id,
            "raw_code": raw_code
        })
        assert confirm_res.status_code == 200
        
        # 4. Request retrieval
        retrieve_res = await client.post("/api/allocations/retrieve-request", json={
            "station_id": station_id,
            "recipient_phone": "+60123456789",
            "pickup_code": raw_code
        })
        assert retrieve_res.status_code == 200
        
        # 5. Complete retrieval (close door)
        slot_id = dep_data["unlocked_slot"]["id"]
        complete_res = await client.post("/api/allocations/retrieve-complete", json={
            "slot_id": slot_id
        })
        assert complete_res.status_code == 200
