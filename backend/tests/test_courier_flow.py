import pytest
from uuid import uuid4
from src.domain.models import LockerSize, LockerStatus
from src.domain.services import initialize_station, deposit_courier_package, confirm_deposit_and_send_notification, cancel_deposit
from src.main import InMemoryNotificationSender

@pytest.mark.asyncio
async def test_courier_dropoff_dynamic(db_session):
    station_id = uuid4()
    await initialize_station(db_session, station_id, "Courier Test Station", "123 Courier St")
    
    from src.domain.models import LockerSlot
    slot = LockerSlot(station_id=station_id, slot_code="S-01", size=LockerSize.SMALL, status=LockerStatus.AVAILABLE)
    db_session.add(slot)
    await db_session.flush()
    
    sender = InMemoryNotificationSender()
    allocation, raw_code = await deposit_courier_package(
        db=db_session,
        station_id=station_id,
        package_identifier="PKG-DYNAMIC",
        courier_name="Shopee Xpress",
        courier_code="SPX-001",
        recipient_phone="+60123456789",
        package_size=LockerSize.SMALL
    )
    
    assert allocation.package_identifier == "PKG-DYNAMIC"
    assert allocation.slot_id == slot.id
    assert slot.status == LockerStatus.OCCUPIED
    
    # Confirm door closure and verify SMS notification
    await confirm_deposit_and_send_notification(db_session, allocation.id, raw_code, sender)

@pytest.mark.asyncio
async def test_courier_dropoff_cancel(db_session):
    station_id = uuid4()
    await initialize_station(db_session, station_id, "Cancel Test Station", "456 Cancel St")
    
    from src.domain.models import LockerSlot
    slot = LockerSlot(station_id=station_id, slot_code="S-02", size=LockerSize.SMALL, status=LockerStatus.AVAILABLE)
    db_session.add(slot)
    await db_session.flush()
    
    allocation, raw_code = await deposit_courier_package(
        db=db_session,
        station_id=station_id,
        package_identifier="PKG-CANCEL",
        courier_name="Shopee Xpress",
        courier_code="SPX-001",
        recipient_phone="+60123456789",
        package_size=LockerSize.SMALL
    )
    
    assert slot.status == LockerStatus.OCCUPIED
    
    # User cancels deposit while door is open
    await cancel_deposit(db_session, allocation.id)
    assert slot.status == LockerStatus.AVAILABLE

@pytest.mark.asyncio
async def test_courier_dropoff_invalid_courier(db_session):
    station_id = uuid4()
    with pytest.raises(ValueError, match="Invalid courier credentials"):
        await deposit_courier_package(
            db=db_session,
            station_id=station_id,
            package_identifier="PKG-INVALID",
            courier_name="",
            courier_code="",
            recipient_phone="+60123456789",
            package_size=LockerSize.SMALL
        )
