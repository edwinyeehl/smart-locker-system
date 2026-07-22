import pytest
from uuid import uuid4
from src.domain.models import LockerStation, LockerSlot, LockerSize, LockerStatus, Allocation, AllocationType
from src.domain.services import initialize_station, deposit_p2p_package, LockerFullException

@pytest.mark.asyncio
async def test_p2p_deposit_success(db_session):
    # Setup station and small slot
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "P2P Mall", "100 P2P Ave")
    
    slot = LockerSlot(
        station_id=station.id,
        slot_code="S-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot)
    await db_session.flush()
    
    # Successful P2P deposit
    storer_name = "Alice Storer"
    storer_phone = "+1112223333"
    recipient_name = "Bob Recipient"
    recipient_phone = "+4445556666"
    
    allocation, raw_code = await deposit_p2p_package(
        db=db_session,
        station_id=station.id,
        package_size=LockerSize.SMALL,
        storer_name=storer_name,
        storer_phone=storer_phone,
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        recipient_email="bob@example.com",
        agreed_to_tc=True,
        payment_amount=10.00  # Base rate is 10.00
    )
    
    assert allocation is not None
    assert allocation.allocation_type == AllocationType.P2P
    assert allocation.storer_name == storer_name
    assert allocation.storer_phone == storer_phone
    assert allocation.recipient_name == recipient_name
    assert allocation.recipient_phone == recipient_phone
    assert allocation.initial_payment_paid == 10.00
    assert len(raw_code) == 6
    
    # Verify slot is occupied
    await db_session.refresh(slot)
    assert slot.status == LockerStatus.OCCUPIED

@pytest.mark.asyncio
async def test_p2p_deposit_no_tc_agreement(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "P2P Mall B", "200 P2P Ave")
    
    # Trying to deposit without T&C agreement should fail
    with pytest.raises(ValueError, match="Must agree to terms and conditions"):
        await deposit_p2p_package(
            db=db_session,
            station_id=station_id,
            package_size=LockerSize.SMALL,
            storer_name="Alice",
            storer_phone="+111",
            recipient_phone="+222",
            agreed_to_tc=False,
            payment_amount=10.00
        )

@pytest.mark.asyncio
async def test_p2p_deposit_insufficient_payment(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "P2P Mall C", "300 P2P Ave")
    
    # Trying to deposit with less than base 10.00 should fail
    with pytest.raises(ValueError, match="Insufficient initial payment"):
        await deposit_p2p_package(
            db=db_session,
            station_id=station_id,
            package_size=LockerSize.SMALL,
            storer_name="Alice",
            storer_phone="+111",
            recipient_phone="+222",
            agreed_to_tc=True,
            payment_amount=5.00  # less than 10.00
        )
