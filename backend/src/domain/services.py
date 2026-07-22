import random
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.domain.models import LockerStation, LockerSlot, Engineer, LockerStatus, LockerSize, Allocation, AllocationType

# Re-export modular domain services for 100% backward compatibility
from src.domain.pricing import calculate_storage_charge, compute_fee_for_days, calculate_duration_days
from src.domain.engineer_service import hash_password, create_engineer, authenticate_engineer
from src.domain.station_service import initialize_station, toggle_slot_maintenance

class LockerFullException(Exception):
    pass

def generate_pickup_code() -> str:
    """Generate a random 6-digit numeric pickup PIN."""
    return "".join(random.choices("0123456789", k=6))

async def deposit_courier_package(
    db: AsyncSession,
    station_id: UUID,
    package_identifier: str,
    courier_name: str,
    courier_code: str,
    recipient_phone: str,
    package_size: LockerSize
) -> tuple[Allocation, str]:
    """Execute dynamic courier package deposit. SMS notification is deferred until door closure."""
    if not courier_code or not courier_name:
        raise ValueError("Invalid courier credentials")
        
    if not recipient_phone or not package_size:
        raise ValueError("Recipient phone number and package size are required")
        
    station_result = await db.execute(select(LockerStation).where(LockerStation.id == station_id))
    station = station_result.scalar_one_or_none()
    if not station:
        raise ValueError("Station not found")
        
    raw_code = generate_pickup_code()
    code_hash = hash_password(raw_code)
    
    size_sequence = [LockerSize.SMALL, LockerSize.MEDIUM, LockerSize.LARGE]
    try:
        start_idx = size_sequence.index(package_size)
    except ValueError:
        raise ValueError("Invalid package size")
        
    candidate_sizes = size_sequence[start_idx:]
    
    selected_slot = None
    for size in candidate_sizes:
        query = select(LockerSlot).where(
            and_(
                LockerSlot.station_id == station_id,
                LockerSlot.size == size,
                LockerSlot.status == LockerStatus.AVAILABLE
            )
        ).limit(1).with_for_update(skip_locked=True)
        result = await db.execute(query)
        selected_slot = result.scalar_one_or_none()
        if selected_slot:
            break
            
    if not selected_slot:
        raise LockerFullException("No available slots to accommodate the package size at this station.")
        
    selected_slot.status = LockerStatus.OCCUPIED
    
    allocation = Allocation(
        slot_id=selected_slot.id,
        package_identifier=package_identifier,
        package_size=package_size,
        allocation_type=AllocationType.COURIER,
        courier_name=courier_name,
        courier_code=courier_code,
        recipient_phone=recipient_phone,
        pickup_code_hash=code_hash,
        stored_at=datetime.now(timezone.utc),
        is_active=True
    )
    db.add(allocation)
    await db.flush()
        
    return allocation, raw_code

async def deposit_p2p_package(
    db: AsyncSession,
    station_id: UUID,
    package_size: LockerSize,
    storer_name: str,
    storer_phone: str,
    recipient_phone: str,
    agreed_to_tc: bool,
    payment_amount: float,
    recipient_name: str | None = None,
    recipient_email: str | None = None
) -> tuple[Allocation, str]:
    """Execute peer-to-peer package deposit with upfront payment validation. SMS notification deferred until door close."""
    if not agreed_to_tc:
        raise ValueError("Must agree to terms and conditions")
        
    base_rate = 10.00
    if payment_amount < base_rate:
        raise ValueError("Insufficient initial payment")
        
    station_result = await db.execute(select(LockerStation).where(LockerStation.id == station_id))
    station = station_result.scalar_one_or_none()
    if not station:
        raise ValueError("Station not found")
        
    size_sequence = [LockerSize.SMALL, LockerSize.MEDIUM, LockerSize.LARGE]
    try:
        start_idx = size_sequence.index(package_size)
    except ValueError:
        raise ValueError("Invalid package size")
        
    candidate_sizes = size_sequence[start_idx:]
    
    selected_slot = None
    for size in candidate_sizes:
        query = select(LockerSlot).where(
            and_(
                LockerSlot.station_id == station_id,
                LockerSlot.size == size,
                LockerSlot.status == LockerStatus.AVAILABLE
            )
        ).limit(1).with_for_update(skip_locked=True)
        result = await db.execute(query)
        selected_slot = result.scalar_one_or_none()
        if selected_slot:
            break
            
    if not selected_slot:
        raise LockerFullException("No available slots to accommodate the package size at this station.")
        
    selected_slot.status = LockerStatus.OCCUPIED
    
    raw_code = generate_pickup_code()
    code_hash = hash_password(raw_code)
    package_identifier = f"P2P-{random.randint(1000, 9999)}"
    
    allocation = Allocation(
        slot_id=selected_slot.id,
        package_identifier=package_identifier,
        package_size=package_size,
        allocation_type=AllocationType.P2P,
        storer_name=storer_name,
        storer_phone=storer_phone,
        recipient_name=recipient_name,
        recipient_phone=recipient_phone,
        recipient_email=recipient_email,
        pickup_code_hash=code_hash,
        stored_at=datetime.now(timezone.utc),
        initial_payment_paid=Decimal(str(payment_amount)),
        is_active=True
    )
    db.add(allocation)
    await db.flush()
        
    return allocation, raw_code

async def confirm_deposit_and_send_notification(
    db: AsyncSession,
    allocation_id: UUID,
    raw_code: str,
    notification_sender = None
) -> Allocation:
    """Confirm deposit door closure and dispatch SMS notification to recipient."""
    query = select(Allocation).where(Allocation.id == allocation_id)
    res = await db.execute(query)
    allocation = res.scalar_one_or_none()
    if not allocation:
        raise ValueError("Allocation not found")
        
    slot_res = await db.execute(select(LockerSlot).where(LockerSlot.id == allocation.slot_id))
    slot = slot_res.scalar_one_or_none()
    
    station_res = await db.execute(select(LockerStation).where(LockerStation.id == slot.station_id)) if slot else None
    station = station_res.scalar_one_or_none() if station_res else None
    
    if notification_sender and slot and station:
        if allocation.allocation_type == AllocationType.COURIER:
            message = (
                f"Your package has been delivered to locker {slot.slot_code} at {station.name}. "
                f"Your pickup code is {raw_code}. The first day is free. "
                "Subsequent days will incur a tiered storage fee of RM10/day."
            )
        else:
            message = (
                f"{allocation.storer_name} has stored a package for you in locker {slot.slot_code} at {station.name}. "
                f"Your pickup code is {raw_code}. Storage is pre-paid for Day 1. "
                "Subsequent days will incur a tiered storage fee of RM10/day."
            )
        await notification_sender.send_pickup_notification(
            recipient_phone=allocation.recipient_phone,
            recipient_email=allocation.recipient_email,
            raw_code=raw_code,
            slot_code=slot.slot_code,
            station_name=station.name,
            message=message
        )
        
    return allocation

async def cancel_deposit(db: AsyncSession, allocation_id: UUID) -> None:
    """Cancel deposit operation while door is open: revert slot to AVAILABLE and delete pending allocation."""
    query = select(Allocation).where(Allocation.id == allocation_id).with_for_update()
    res = await db.execute(query)
    allocation = res.scalar_one_or_none()
    if not allocation:
        raise ValueError("Allocation not found")
        
    slot_res = await db.execute(select(LockerSlot).where(LockerSlot.id == allocation.slot_id).with_for_update())
    slot = slot_res.scalar_one_or_none()
    if slot:
        slot.status = LockerStatus.AVAILABLE
        
    await db.delete(allocation)
    await db.flush()

async def request_package_retrieval(
    db: AsyncSession,
    station_id: UUID,
    recipient_phone: str,
    pickup_code: str
) -> Allocation:
    """Validate recipient pickup PIN, calculate storage charges due, and lock allocation."""
    hashed_code = hash_password(pickup_code)
    
    query = select(Allocation).join(LockerSlot).where(
        and_(
            LockerSlot.station_id == station_id,
            Allocation.recipient_phone == recipient_phone,
            Allocation.pickup_code_hash == hashed_code,
            Allocation.is_active == True
        )
    ).with_for_update()
    result = await db.execute(query)
    allocation = result.scalar_one_or_none()
    
    if not allocation:
        raise ValueError("Invalid pickup code or phone number")
        
    charge = await calculate_storage_charge(db, allocation.id)
    allocation.total_charge_applied = Decimal(str(charge))
    await db.flush()
    
    return allocation

async def complete_package_retrieval(
    db: AsyncSession,
    slot_id: UUID
) -> Allocation:
    """Complete package retrieval when door close sensor triggers, marking slot AVAILABLE."""
    query = select(Allocation).where(
        and_(
            Allocation.slot_id == slot_id,
            Allocation.is_active == True
        )
    ).with_for_update()
    result = await db.execute(query)
    allocation = result.scalar_one_or_none()
    
    if not allocation:
        raise ValueError("No active allocation for this slot")
        
    allocation.is_active = False
    allocation.retrieved_at = datetime.now(timezone.utc)
    
    slot_result = await db.execute(
        select(LockerSlot).where(LockerSlot.id == slot_id).with_for_update()
    )
    slot = slot_result.scalar_one_or_none()
    if slot:
        slot.status = LockerStatus.AVAILABLE
        
    await db.flush()
    return allocation
