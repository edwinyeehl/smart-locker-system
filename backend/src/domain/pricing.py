import math
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import Allocation

# Pricing Tier Constants (in RM)
TIER_1_RATE = 10.0  # Days 2 - 5
TIER_2_RATE = 20.0  # Days 6 - 10
TIER_3_RATE = 30.0  # Days 11+

def calculate_duration_days(stored_at: datetime, retrieved_at: datetime | None = None) -> int:
    """Calculate storage duration in calendar days (ceil of hours / 24)."""
    end_time = retrieved_at if retrieved_at else datetime.now(timezone.utc)
    delta = end_time - stored_at
    duration_hours = max(0.0, delta.total_seconds() / 3600.0)
    return math.ceil(duration_hours / 24.0)

def compute_fee_for_days(days: int) -> float:
    """
    Compute tiered storage fee based on total duration in days.
    Day 1 is free/prepaid.
    Days 2 to 5: RM 10/day
    Days 6 to 10: RM 20/day
    Days 11+: RM 30/day
    """
    if days <= 1:
        return 0.00
        
    fee = 0.0
    for day_num in range(2, days + 1):
        if 2 <= day_num <= 5:
            fee += TIER_1_RATE
        elif 6 <= day_num <= 10:
            fee += TIER_2_RATE
        else:
            fee += TIER_3_RATE
            
    return fee

async def calculate_storage_charge(db: AsyncSession, allocation_id: UUID) -> float:
    """Fetch allocation from database and calculate total storage charge due."""
    result = await db.execute(select(Allocation).where(Allocation.id == allocation_id))
    allocation = result.scalar_one_or_none()
    if not allocation:
        raise ValueError("Allocation not found")
        
    days = calculate_duration_days(allocation.stored_at, allocation.retrieved_at)
    return compute_fee_for_days(days)
