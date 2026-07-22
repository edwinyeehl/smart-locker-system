import pytest
from uuid import uuid4
from src.domain.models import LockerSize, LockerStatus
from src.domain.services import initialize_station, deposit_courier_package, deposit_p2p_package, confirm_deposit_and_send_notification
from src.main import InMemoryNotificationSender

@pytest.mark.asyncio
async def test_notification_sent_on_courier_deposit_confirm(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "Notif Station", "123 Notif St")
    
    from src.domain.models import LockerSlot
    slot = LockerSlot(station_id=station_id, slot_code="S-01", size=LockerSize.SMALL, status=LockerStatus.AVAILABLE)
    db_session.add(slot)
    await db_session.flush()
    
    sender = InMemoryNotificationSender()
    allocation, raw_code = await deposit_courier_package(
        db=db_session,
        station_id=station_id,
        package_identifier="PKG-NOTIF",
        courier_name="Shopee Xpress",
        courier_code="SPX-001",
        recipient_phone="+60123456789",
        package_size=LockerSize.SMALL
    )
    
    # Confirm door closure and verify notification is sent
    await confirm_deposit_and_send_notification(db_session, allocation.id, raw_code, sender)
    from src.main import notifications_log
    assert len(notifications_log) > 0
    latest = notifications_log[-1]
    assert latest["recipient_phone"] == "+60123456789"
    assert latest["raw_code"] == raw_code
    assert "RM10/day" in latest["message"]

@pytest.mark.asyncio
async def test_notification_sent_on_p2p_deposit_confirm(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "Notif Station P2P", "456 Notif St")
    
    from src.domain.models import LockerSlot
    slot = LockerSlot(station_id=station_id, slot_code="S-02", size=LockerSize.SMALL, status=LockerStatus.AVAILABLE)
    db_session.add(slot)
    await db_session.flush()
    
    sender = InMemoryNotificationSender()
    allocation, raw_code = await deposit_p2p_package(
        db=db_session,
        station_id=station_id,
        package_size=LockerSize.SMALL,
        storer_name="Alice",
        storer_phone="+60198765432",
        recipient_phone="+60123456789",
        agreed_to_tc=True,
        payment_amount=10.00
    )
    
    await confirm_deposit_and_send_notification(db_session, allocation.id, raw_code, sender)
    from src.main import notifications_log
    latest = notifications_log[-1]
    assert latest["recipient_phone"] == "+60123456789"
    assert latest["raw_code"] == raw_code
