import pytest
from uuid import uuid4
from src.domain.models import LockerStation, LockerSlot, LockerSize, LockerStatus, Allocation, AllocationType
from src.domain.services import (
    initialize_station,
    deposit_courier_package,
    request_package_retrieval,
    complete_package_retrieval,
    LockerFullException
)

@pytest.mark.asyncio
async def test_retrieve_package_success(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "South Mall", "456 Oak Rd")
    
    slot = LockerSlot(
        station_id=station.id,
        slot_code="S-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot)
    await db_session.flush()
    
    # Deposit a package
    recipient_phone = "+1234567890"
    allocation, raw_code = await deposit_courier_package(
        db=db_session,
        station_id=station.id,
        package_identifier="PKG-111",
        courier_name="UPS",
        courier_code="UPS-123",
        recipient_phone=recipient_phone,
        package_size=LockerSize.SMALL
    )
    
    # Request retrieval (unlock request)
    retrieved_allocation = await request_package_retrieval(
        db=db_session,
        station_id=station.id,
        recipient_phone=recipient_phone,
        pickup_code=raw_code
    )
    
    assert retrieved_allocation is not None
    assert retrieved_allocation.id == allocation.id
    assert retrieved_allocation.slot_id == slot.id
    
    # During request_package_retrieval, the door opens, but slot stays OCCUPIED until door closes
    await db_session.refresh(slot)
    assert slot.status == LockerStatus.OCCUPIED
    assert retrieved_allocation.is_active is True
    
    # Simulate closing the physical door to complete the retrieval
    completed_allocation = await complete_package_retrieval(
        db=db_session,
        slot_id=slot.id
    )
    
    assert completed_allocation.is_active is False
    assert completed_allocation.retrieved_at is not None
    
    # Slot should now be AVAILABLE
    await db_session.refresh(slot)
    assert slot.status == LockerStatus.AVAILABLE

@pytest.mark.asyncio
async def test_retrieve_package_invalid_code(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "South Mall B", "456 Oak Rd")
    
    slot = LockerSlot(
        station_id=station.id,
        slot_code="S-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot)
    await db_session.flush()
    
    recipient_phone = "+1234567890"
    await deposit_courier_package(
        db=db_session,
        station_id=station.id,
        package_identifier="PKG-222",
        courier_name="UPS",
        courier_code="UPS-123",
        recipient_phone=recipient_phone,
        package_size=LockerSize.SMALL
    )
    
    # Wrong code should raise ValueError
    with pytest.raises(ValueError, match="Invalid pickup code or phone number"):
        await request_package_retrieval(
            db=db_session,
            station_id=station.id,
            recipient_phone=recipient_phone,
            pickup_code="999999"
        )

@pytest.mark.asyncio
async def test_retrieve_package_wrong_phone(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "South Mall C", "456 Oak Rd")
    
    slot = LockerSlot(
        station_id=station.id,
        slot_code="S-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot)
    await db_session.flush()
    
    recipient_phone = "+1234567890"
    allocation, raw_code = await deposit_courier_package(
        db=db_session,
        station_id=station.id,
        package_identifier="PKG-333",
        courier_name="UPS",
        courier_code="UPS-123",
        recipient_phone=recipient_phone,
        package_size=LockerSize.SMALL
    )
    
    # Correct code but wrong phone should raise ValueError
    with pytest.raises(ValueError, match="Invalid pickup code or phone number"):
        await request_package_retrieval(
            db=db_session,
            station_id=station.id,
            recipient_phone="+999999999",
            pickup_code=raw_code
        )

@pytest.mark.asyncio
async def test_retrieve_package_wrong_station(db_session):
    station_a_id = uuid4()
    station_a = await initialize_station(db_session, station_a_id, "Station A", "1 Main St")
    
    slot_a = LockerSlot(
        station_id=station_a.id,
        slot_code="S-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot_a)
    await db_session.flush()
    
    # Deposit package at Station A
    recipient_phone = "+1234567890"
    allocation, raw_code = await deposit_courier_package(
        db=db_session,
        station_id=station_a.id,
        package_identifier="PKG-444",
        courier_name="UPS",
        courier_code="UPS-123",
        recipient_phone=recipient_phone,
        package_size=LockerSize.SMALL
    )
    
    # Try to retrieve it at Station B (different station ID)
    station_b_id = uuid4()
    station_b = await initialize_station(db_session, station_b_id, "Station B", "2 Main St")
    
    with pytest.raises(ValueError, match="Invalid pickup code or phone number"):
        await request_package_retrieval(
            db=db_session,
            station_id=station_b.id,
            recipient_phone=recipient_phone,
            pickup_code=raw_code
        )
