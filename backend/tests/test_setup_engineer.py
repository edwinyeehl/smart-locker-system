import pytest
from uuid import uuid4
from sqlalchemy import select
from src.core.database import Base
from src.domain.models import LockerStation, LockerSlot, Engineer, LockerSize, LockerStatus
from src.domain.services import initialize_station, toggle_slot_maintenance, authenticate_engineer, create_engineer

@pytest.mark.asyncio
async def test_initialize_station(db_session):
    # Target behavior: An engineer can initialize a locker station with a name and address
    station_id = uuid4()
    station = await initialize_station(
        db=db_session,
        station_id=station_id,
        name="Downtown Mall Station",
        address="123 Main St"
    )
    
    assert station is not None
    assert station.id == station_id
    assert station.name == "Downtown Mall Station"
    assert station.address == "123 Main St"

@pytest.mark.asyncio
async def test_create_and_authenticate_engineer(db_session):
    # Target behavior: Engineers can be created and authenticated with a unique username and password
    username = "tech_bob"
    password = "securepassword123"
    code = "ENG-007"
    
    engineer = await create_engineer(
        db=db_session,
        username=username,
        password=password,
        engineer_code=code
    )
    
    assert engineer is not None
    assert engineer.username == username
    assert engineer.engineer_code == code
    
    # Verify successful authentication
    authenticated = await authenticate_engineer(
        db=db_session,
        username=username,
        password=password
    )
    assert authenticated is not None
    assert authenticated.id == engineer.id
    
    # Verify authentication fails with incorrect password
    failed_auth = await authenticate_engineer(
        db=db_session,
        username=username,
        password="wrongpassword"
    )
    assert failed_auth is None

@pytest.mark.asyncio
async def test_toggle_slot_maintenance_mode(db_session):
    # Target behavior: An authenticated engineer can toggle a slot's status to MAINTENANCE (rendering it unusable)
    station_id = uuid4()
    station = await initialize_station(
        db=db_session,
        station_id=station_id,
        name="Station A",
        address="Address A"
    )
    
    # Create an available slot
    slot = LockerSlot(
        station_id=station.id,
        slot_code="A-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot)
    await db_session.flush()
    
    # Create and authenticate an engineer
    engineer = await create_engineer(
        db=db_session,
        username="tech_alice",
        password="password123",
        engineer_code="ENG-123"
    )
    
    # Toggle to maintenance mode
    updated_slot = await toggle_slot_maintenance(
        db=db_session,
        slot_id=slot.id,
        engineer_id=engineer.id
    )
    
    assert updated_slot.status == LockerStatus.MAINTENANCE
    
    # Toggle back to available
    reverted_slot = await toggle_slot_maintenance(
        db=db_session,
        slot_id=slot.id,
        engineer_id=engineer.id
    )
    assert reverted_slot.status == LockerStatus.AVAILABLE
