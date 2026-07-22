import hashlib
from src.domain.engineer_service import hash_password
from src.domain.services import generate_pickup_code

def test_hash_password():
    """Verify SHA-256 password hashing helper output."""
    raw = "admin123"
    expected = hashlib.sha256(raw.encode()).hexdigest()
    assert hash_password(raw) == expected

def test_generate_pickup_code():
    """Verify pickup PIN generation is 6 numeric digits."""
    code = generate_pickup_code()
    assert len(code) == 6
    assert code.isdigit()
