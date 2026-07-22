from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import LockerStation, LockerSlot, Engineer, LockerStatus

async def initialize_station(db: AsyncSession, station_id: UUID, name: str, address: str) -> LockerStation:
    """Initialize a new physical locker station."""
    station = LockerStation(id=station_id, name=name, address=address)
    db.add(station)
    await db.flush()
    return station

async def toggle_slot_maintenance(db: AsyncSession, slot_id: UUID, engineer_id: UUID) -> LockerSlot:
    """Toggle maintenance status on a locker slot with engineer verification and row locking."""
    # Confirm engineer existence
    engineer_result = await db.execute(select(Engineer).where(Engineer.id == engineer_id))
    engineer = engineer_result.scalar_one_or_none()
    if not engineer:
        raise ValueError("Invalid engineer ID")
        
    # Lock slot row during toggle update to avoid concurrent state collisions
    slot_result = await db.execute(
        select(LockerSlot).where(LockerSlot.id == slot_id).with_for_update()
    )
    slot = slot_result.scalar_one_or_none()
    if not slot:
        raise ValueError("Slot not found")
        
    if slot.status == LockerStatus.MAINTENANCE:
        slot.status = LockerStatus.AVAILABLE
    else:
        slot.status = LockerStatus.MAINTENANCE
        
    await db.flush()
    return slot
