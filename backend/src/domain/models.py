import enum
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, ForeignKey, Enum, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from src.core.database import Base

class LockerSize(str, enum.Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"

class LockerStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"

class AllocationType(str, enum.Enum):
    COURIER = "COURIER"
    P2P = "P2P"

class LockerStation(Base):
    __tablename__ = "locker_stations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(100), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Engineer(Base):
    __tablename__ = "engineers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    engineer_code = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class LockerSlot(Base):
    __tablename__ = "locker_slots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    station_id = Column(UUID(as_uuid=True), ForeignKey("locker_stations.id", ondelete="CASCADE"), nullable=False)
    slot_code = Column(String(10), nullable=False)
    size = Column(Enum(LockerSize, name="locker_size"), nullable=False)
    status = Column(Enum(LockerStatus, name="locker_status"), server_default="AVAILABLE", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("station_id", "slot_code", name="uq_station_slot_code"),
    )

class Allocation(Base):
    __tablename__ = "allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    slot_id = Column(UUID(as_uuid=True), ForeignKey("locker_slots.id", ondelete="RESTRICT"), nullable=False)
    package_identifier = Column(String(100), nullable=False)
    package_size = Column(Enum(LockerSize, name="locker_size"), nullable=False)
    allocation_type = Column(Enum(AllocationType, name="allocation_type"), server_default="COURIER", nullable=False)
    
    courier_name = Column(String(100), nullable=True)
    courier_code = Column(String(50), nullable=True)
    storer_name = Column(String(100), nullable=True)
    storer_phone = Column(String(50), nullable=True)
    
    recipient_name = Column(String(100), nullable=True)
    recipient_phone = Column(String(50), nullable=False)
    recipient_email = Column(String(255), nullable=True)
    
    pickup_code_hash = Column(String(255), nullable=True)
    
    stored_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    retrieved_at = Column(DateTime(timezone=True), nullable=True)
    reservation_expires_at = Column(DateTime(timezone=True), nullable=True)
    initial_payment_paid = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    total_charge_applied = Column(Numeric(10, 2), server_default="0.00", nullable=False)
    is_active = Column(Boolean, server_default="true", nullable=False)
