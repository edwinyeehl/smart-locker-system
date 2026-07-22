import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from freezegun import freeze_time
from src.domain.models import LockerStation, LockerSlot, LockerSize, LockerStatus, Allocation, AllocationType
from src.domain.services import (
    initialize_station,
    deposit_courier_package,
    deposit_p2p_package,
    request_package_retrieval,
    calculate_storage_charge
)

@pytest.mark.asyncio
async def test_courier_pricing_free_window(db_session):
    # Free window check (within 24 hours of deposit, fee is 0.00)
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
    
    initial_time = datetime(2026, 7, 21, 10, 0, 0, tzinfo=timezone.utc)
    
    with freeze_time(initial_time) as frozen_datetime:
        allocation, raw_code = await deposit_courier_package(
            db=db_session,
            station_id=station.id,
            package_identifier="PKG-1",
            courier_name="UPS",
            courier_code="UPS-123",
            recipient_phone="+1234567890",
            package_size=LockerSize.SMALL
        )
        
        # 1. Check charge immediately after deposit (0 hours)
        charge = await calculate_storage_charge(db_session, allocation.id)
        assert charge == 0.00
        
        # 2. Move time forward by 12 hours (within 24h)
        frozen_datetime.move_to(initial_time + timedelta(hours=12))
        charge_12h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_12h == 0.00
        
        # 3. Move time forward by exactly 24 hours (within 24h boundary)
        frozen_datetime.move_to(initial_time + timedelta(hours=24))
        charge_24h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_24h == 0.00

@pytest.mark.asyncio
async def test_courier_pricing_tiered_fees(db_session):
    station_id = uuid4()
    station = await initialize_station(db_session, station_id, "Central Mall", "12 Broadway")
    
    slot = LockerSlot(
        station_id=station.id,
        slot_code="S-01",
        size=LockerSize.SMALL,
        status=LockerStatus.AVAILABLE
    )
    db_session.add(slot)
    await db_session.flush()
    
    initial_time = datetime(2026, 7, 21, 10, 0, 0, tzinfo=timezone.utc)
    
    with freeze_time(initial_time) as frozen_datetime:
        allocation, raw_code = await deposit_courier_package(
            db=db_session,
            station_id=station.id,
            package_identifier="PKG-2",
            courier_name="UPS",
            courier_code="UPS-123",
            recipient_phone="+1234567890",
            package_size=LockerSize.SMALL
        )
        
        # 1. Day 2 collection (between 24h and 48h, e.g. 26 hours -> 2 days total)
        # Day 1: Free
        # Day 2: 10.00
        frozen_datetime.move_to(initial_time + timedelta(hours=26))
        charge_26h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_26h == 10.00
        
        # 2. Day 5 collection (e.g. 100 hours -> 5 days total)
        # Day 1: Free
        # Days 2-5: 4 days * 10.00 = 40.00
        frozen_datetime.move_to(initial_time + timedelta(hours=100))
        charge_100h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_100h == 40.00
        
        # 3. Day 6 collection (e.g. 125 hours -> 6 days total)
        # Day 1: Free
        # Days 2-5: 4 days * 10.00 = 40.00
        # Day 6: 1 day * 20.00 = 20.00
        # Total: 60.00
        frozen_datetime.move_to(initial_time + timedelta(hours=125))
        charge_125h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_125h == 60.00
        
        # 4. Day 11 collection (e.g. 245 hours -> 11 days total)
        # Day 1: Free
        # Days 2-5: 4 days * 10.00 = 40.00
        # Days 6-10: 5 days * 20.00 = 100.00
        # Day 11: 1 day * 30.00 = 30.00
        # Total: 170.00
        frozen_datetime.move_to(initial_time + timedelta(hours=245))
        charge_245h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_245h == 170.00

@pytest.mark.asyncio
async def test_p2p_pricing_upfront_offset(db_session):
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
    
    initial_time = datetime(2026, 7, 21, 10, 0, 0, tzinfo=timezone.utc)
    
    with freeze_time(initial_time) as frozen_datetime:
        allocation, raw_code = await deposit_p2p_package(
            db=db_session,
            station_id=station.id,
            package_size=LockerSize.SMALL,
            storer_name="Alice Storer",
            storer_phone="+1112223333",
            recipient_phone="+4445556666",
            agreed_to_tc=True,
            payment_amount=10.00  # Day 1 paid upfront
        )
        
        # 1. Day 1 collection (within 24 hours, e.g. 12 hours)
        # Storer paid Day 1 upfront (10.00), so recipient owes 0.00 extra
        frozen_datetime.move_to(initial_time + timedelta(hours=12))
        charge_12h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_12h == 0.00
        
        # 2. Day 2 collection (e.g. 30 hours -> 2 days total)
        # Day 1: Covered by upfront (10.00)
        # Day 2: 10.00 (owed by recipient)
        frozen_datetime.move_to(initial_time + timedelta(hours=30))
        charge_30h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_30h == 10.00
        
        # 3. Day 6 collection (e.g. 125 hours -> 6 days total)
        # Day 1: Covered by upfront (10.00)
        # Days 2-5: 4 days * 10.00 = 40.00
        # Day 6: 1 day * 20.00 = 20.00
        # Total extra owed: 60.00
        frozen_datetime.move_to(initial_time + timedelta(hours=125))
        charge_125h = await calculate_storage_charge(db_session, allocation.id)
        assert charge_125h == 60.00
