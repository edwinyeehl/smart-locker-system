import os
from uuid import UUID, uuid4
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.core.database import get_db, Base
from src.domain.models import LockerStation, LockerSlot, Engineer, Allocation, LockerSize, LockerStatus, AllocationType
from src.domain.services import (
    initialize_station as service_initialize_station,
    create_engineer as service_create_engineer,
    authenticate_engineer as service_authenticate_engineer,
    toggle_slot_maintenance as service_toggle_slot_maintenance,
    deposit_courier_package as service_deposit_courier_package,
    deposit_p2p_package as service_deposit_p2p_package,
    confirm_deposit_and_send_notification as service_confirm_deposit,
    cancel_deposit as service_cancel_deposit,
    request_package_retrieval as service_request_package_retrieval,
    complete_package_retrieval as service_complete_package_retrieval,
    calculate_storage_charge as service_calculate_storage_charge,
    LockerFullException
)

app = FastAPI(title="Smart Locker Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Notification log enqueuer
notifications_log = []

class InMemoryNotificationSender:
    async def send_pickup_notification(
        self,
        recipient_phone: str,
        recipient_email: Optional[str],
        raw_code: str,
        slot_code: str,
        station_name: str,
        message: str
    ) -> None:
        notifications_log.append({
            "id": str(uuid4()),
            "recipient_phone": recipient_phone,
            "recipient_email": recipient_email,
            "raw_code": raw_code,
            "slot_code": slot_code,
            "station_name": station_name,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

notification_sender = InMemoryNotificationSender()

# --- Pydantic Schemas ---

class StationCreate(BaseModel):
    name: str
    address: str
    station_id: Optional[UUID] = None
    seed_slots: Optional[bool] = True

class EngineerCreate(BaseModel):
    username: str
    password: str
    engineer_code: str

class EngineerLogin(BaseModel):
    username: str
    password: str

class ToggleMaintenanceRequest(BaseModel):
    engineer_id: UUID

class CourierDepositRequest(BaseModel):
    station_id: UUID
    package_identifier: str
    courier_name: str
    courier_code: str
    recipient_phone: str
    package_size: LockerSize

class P2PDepositRequest(BaseModel):
    station_id: UUID
    package_size: LockerSize
    storer_name: str
    storer_phone: str
    recipient_phone: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    agreed_to_tc: bool
    payment_amount: float

class ConfirmDepositRequest(BaseModel):
    allocation_id: UUID
    raw_code: str

class CancelDepositRequest(BaseModel):
    allocation_id: UUID

class RetrievalRequest(BaseModel):
    station_id: UUID
    recipient_phone: str
    pickup_code: str

class CompleteRetrievalRequest(BaseModel):
    slot_id: UUID

# --- API Routes ---

@app.get("/api/stations")
async def get_stations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LockerStation))
    stations = result.scalars().all()
    return stations

@app.post("/api/stations/initialize")
async def initialize_station(payload: StationCreate, db: AsyncSession = Depends(get_db)):
    station_id = payload.station_id or uuid4()
    try:
        station = await service_initialize_station(db, station_id, payload.name, payload.address)
        if payload.seed_slots:
            slot_definitions = [
                ("S-01", LockerSize.SMALL),
                ("S-02", LockerSize.SMALL),
                ("S-03", LockerSize.SMALL),
                ("M-01", LockerSize.MEDIUM),
                ("M-02", LockerSize.MEDIUM),
                ("L-01", LockerSize.LARGE)
            ]
            for slot_code, size in slot_definitions:
                slot = LockerSlot(
                    station_id=station.id,
                    slot_code=slot_code,
                    size=size,
                    status=LockerStatus.AVAILABLE
                )
                db.add(slot)
            await db.flush()
            
        await db.commit()
        return station
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/stations/{station_id}/slots")
async def get_station_slots(station_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LockerSlot).where(LockerSlot.station_id == station_id).order_by(LockerSlot.slot_code)
    )
    slots = result.scalars().all()
    return slots

@app.post("/api/slots/{slot_id}/toggle-maintenance")
async def toggle_slot_maintenance(slot_id: UUID, payload: ToggleMaintenanceRequest, db: AsyncSession = Depends(get_db)):
    try:
        slot = await service_toggle_slot_maintenance(db, slot_id, payload.engineer_id)
        await db.commit()
        return slot
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/engineers/create")
async def create_engineer(payload: EngineerCreate, db: AsyncSession = Depends(get_db)):
    try:
        engineer = await service_create_engineer(db, payload.username, payload.password, payload.engineer_code)
        await db.commit()
        return {"id": engineer.id, "username": engineer.username, "engineer_code": engineer.engineer_code}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/engineers/login")
async def login_engineer(payload: EngineerLogin, db: AsyncSession = Depends(get_db)):
    engineer = await service_authenticate_engineer(db, payload.username, payload.password)
    if not engineer:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"id": engineer.id, "username": engineer.username, "engineer_code": engineer.engineer_code}

@app.post("/api/allocations/deposit-courier")
async def deposit_courier_package(payload: CourierDepositRequest, db: AsyncSession = Depends(get_db)):
    try:
        allocation, raw_code = await service_deposit_courier_package(
            db=db,
            station_id=payload.station_id,
            package_identifier=payload.package_identifier,
            courier_name=payload.courier_name,
            courier_code=payload.courier_code,
            recipient_phone=payload.recipient_phone,
            package_size=payload.package_size
        )
        await db.commit()
        
        slot_result = await db.execute(select(LockerSlot).where(LockerSlot.id == allocation.slot_id))
        slot = slot_result.scalar_one()
        
        return {
            "allocation": allocation,
            "raw_pickup_code": raw_code,
            "unlocked_slot": {
                "id": slot.id,
                "slot_code": slot.slot_code,
                "size": slot.size
            }
        }
    except LockerFullException as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/allocations/deposit-p2p")
async def deposit_p2p_package(payload: P2PDepositRequest, db: AsyncSession = Depends(get_db)):
    try:
        allocation, raw_code = await service_deposit_p2p_package(
            db=db,
            station_id=payload.station_id,
            package_size=payload.package_size,
            storer_name=payload.storer_name,
            storer_phone=payload.storer_phone,
            recipient_phone=payload.recipient_phone,
            agreed_to_tc=payload.agreed_to_tc,
            payment_amount=payload.payment_amount,
            recipient_name=payload.recipient_name,
            recipient_email=payload.recipient_email
        )
        await db.commit()
        
        slot_result = await db.execute(select(LockerSlot).where(LockerSlot.id == allocation.slot_id))
        slot = slot_result.scalar_one()
        
        return {
            "allocation": allocation,
            "raw_pickup_code": raw_code,
            "unlocked_slot": {
                "id": slot.id,
                "slot_code": slot.slot_code,
                "size": slot.size
            }
        }
    except LockerFullException as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/allocations/deposit-confirm")
async def confirm_deposit(payload: ConfirmDepositRequest, db: AsyncSession = Depends(get_db)):
    try:
        allocation = await service_confirm_deposit(
            db=db,
            allocation_id=payload.allocation_id,
            raw_code=payload.raw_code,
            notification_sender=notification_sender
        )
        await db.commit()
        return allocation
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/allocations/deposit-cancel")
async def cancel_deposit(payload: CancelDepositRequest, db: AsyncSession = Depends(get_db)):
    try:
        await service_cancel_deposit(db, payload.allocation_id)
        await db.commit()
        return {"message": "Deposit cancelled successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/allocations/retrieve-request")
async def request_package_retrieval(payload: RetrievalRequest, db: AsyncSession = Depends(get_db)):
    try:
        allocation = await service_request_package_retrieval(
            db=db,
            station_id=payload.station_id,
            recipient_phone=payload.recipient_phone,
            pickup_code=payload.pickup_code
        )
        await db.commit()
        
        slot_result = await db.execute(select(LockerSlot).where(LockerSlot.id == allocation.slot_id))
        slot = slot_result.scalar_one()
        
        return {
            "allocation": allocation,
            "total_charge_applied": allocation.total_charge_applied,
            "unlocked_slot": {
                "id": slot.id,
                "slot_code": slot.slot_code,
                "size": slot.size
            }
        }
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/allocations/retrieve-complete")
async def complete_package_retrieval(payload: CompleteRetrievalRequest, db: AsyncSession = Depends(get_db)):
    try:
        allocation = await service_complete_package_retrieval(db, payload.slot_id)
        await db.commit()
        return allocation
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/notifications")
async def get_notifications():
    return notifications_log

@app.post("/api/notifications/clear")
async def clear_notifications():
    notifications_log.clear()
    return {"message": "Notifications cleared"}
