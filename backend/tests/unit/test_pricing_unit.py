import pytest
from datetime import datetime, timezone, timedelta
from src.domain.pricing import compute_fee_for_days, calculate_duration_days

def test_compute_fee_day_1_free():
    """Day 1 storage is free/prepaid (0 RM fee)."""
    assert compute_fee_for_days(0) == 0.00
    assert compute_fee_for_days(1) == 0.00

def test_compute_fee_tier_1_days_2_to_5():
    """Days 2 to 5 bill RM 10/day."""
    # Day 2: 1 billable day at RM 10 = 10.0
    assert compute_fee_for_days(2) == 10.00
    # Day 3: 2 billable days at RM 10 = 20.0
    assert compute_fee_for_days(3) == 20.00
    # Day 5: 4 billable days at RM 10 = 40.0
    assert compute_fee_for_days(5) == 40.00

def test_compute_fee_tier_2_days_6_to_10():
    """Days 6 to 10 bill RM 20/day."""
    # Day 6: RM 40 (for days 2-5) + RM 20 (for day 6) = 60.0
    assert compute_fee_for_days(6) == 60.00
    # Day 10: RM 40 (days 2-5) + 5 * RM 20 (days 6-10) = 140.0
    assert compute_fee_for_days(10) == 140.00

def test_compute_fee_tier_3_days_11_plus():
    """Days 11+ bill RM 30/day."""
    # Day 11: RM 140 (for days 2-10) + RM 30 = 170.0
    assert compute_fee_for_days(11) == 170.00
    # Day 12: RM 170 + RM 30 = 200.0
    assert compute_fee_for_days(12) == 200.00

def test_calculate_duration_days_ceil():
    """Duration hours ceil to full 24h days."""
    now = datetime.now(timezone.utc)
    
    # 2 hours storage -> 1 day
    stored_2h_ago = now - timedelta(hours=2)
    assert calculate_duration_days(stored_2h_ago, now) == 1
    
    # 24.5 hours storage -> 2 days
    stored_24_5h_ago = now - timedelta(hours=24, minutes=30)
    assert calculate_duration_days(stored_24_5h_ago, now) == 2
