import asyncio
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.database import Base, DATABASE_URL
from src.domain.models import LockerStation, LockerSlot, LockerSize, LockerStatus, Allocation
from src.domain.services import initialize_station, deposit_courier_package, LockerFullException

@pytest.mark.asyncio
async def test_concurrent_slot_allocation(db_engine):
    # We need a separate session maker to run tasks in separate transactions/connections
    session_maker = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # 1. Initialize station and exactly ONE small slot
    station_id = uuid4()
    async with session_maker() as session:
        async with session.begin():
            await initialize_station(session, station_id, "Concurrency Station", "777 Limit St")
            slot = LockerSlot(
                station_id=station_id,
                slot_code="S-01",
                size=LockerSize.SMALL,
                status=LockerStatus.AVAILABLE
            )
            session.add(slot)
            
    # 2. Define two concurrent tasks trying to deposit at the same time
    async def task(package_id: str, recipient_phone: str):
        # Each task runs in its own session/transaction
        async with session_maker() as session:
            try:
                # We start a transaction block
                async with session.begin():
                    allocation, raw_code = await deposit_courier_package(
                        db=session,
                        station_id=station_id,
                        package_identifier=package_id,
                        courier_name="CourierX",
                        courier_code="CX-1",
                        recipient_phone=recipient_phone,
                        package_size=LockerSize.SMALL
                    )
                return True, allocation.id
            except LockerFullException:
                return False, None
            except Exception as e:
                # Return exception details for troubleshooting
                return False, str(e)
                
    # 3. Gather both tasks concurrently
    results = await asyncio.gather(
        task("PKG-CONC-1", "+111"),
        task("PKG-CONC-2", "+222")
    )
    
    # 4. Verify that exactly ONE succeeded and ONE failed
    success_count = sum(1 for success, _ in results if success)
    failure_count = sum(1 for success, _ in results if not success)
    
    assert success_count == 1
    assert failure_count == 1
    
    # Verify the database state has exactly one active allocation
    async with session_maker() as session:
        result = await session.execute(
            select_query := select(Allocation).join(LockerSlot).where(
                LockerSlot.station_id == station_id
            )
        )
        allocations = result.scalars().all()
        assert len(allocations) == 1
        
        # Verify the slot status is OCCUPIED
        slot_result = await session.execute(
            select(LockerSlot).where(LockerSlot.station_id == station_id)
        )
        slot = slot_result.scalar_one()
        assert slot.status == LockerStatus.OCCUPIED

# Import select here for DB verify
from sqlalchemy import select
