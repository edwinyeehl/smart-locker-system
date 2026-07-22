# 🧡 Smart Package Locker System

A full-stack, enterprise-grade Smart Locker Management System and visual terminal simulator built with **FastAPI**, **Next.js (App Router)**, **PostgreSQL**, and **Alembic**.

---

## ⚡ Quickstart (One Command Spin-up)

Spin up the entire application stack (PostgreSQL database, auto-migrating FastAPI backend using `uv`, and Next.js frontend using `npm run dev`) with a single command:

```bash
docker compose up --build -d
```

### Access Endpoints

- 🎨 **Interactive Terminal Simulator (Frontend)**: [http://localhost:3000](http://localhost:3000)
- ⚡ **FastAPI Swagger API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🗄️ **PostgreSQL Database**: `localhost:5432` (`POSTGRES_DB=smart_locker`)

To view live application logs:

```bash
docker compose logs -f
```

To stop all services:

```bash
docker compose down
```

---

## 💻 Manual Local Development Commands

If developing locally outside of Docker:

### 1. Database Setup

Ensure PostgreSQL is running on port 5432 (e.g. `docker compose up -d db`).

### 2. Backend (`backend/`)

Uses `uv` for python dependency management and server execution:

```bash
cd backend
uv run alembic upgrade head
uv run fastapi dev
```

### 3. Frontend (`frontend/`)

Uses Next.js dev server:

```bash
cd frontend
npm run dev
```

---

## 🏗️ Architectural Overview & Core Engineering Decisions

### 1. Modular Domain Layer & Separation of Concerns (SoC)

The backend architecture follows Domain-Driven Design (DDD) principles:

- **`backend/src/domain/pricing.py`**: Isolated storage pricing engine that computes calendar-day storage durations and tiered fee structures.
- **`backend/src/domain/station_service.py`**: Handles locker station creation and engineer-verified slot maintenance toggles.
- **`backend/src/domain/engineer_service.py`**: Handles SHA-256 credential hashing and engineer authentication.
- **`backend/src/domain/services.py`**: Core domain allocation orchestration layer, maintaining 100% backward compatibility.

### 2. ACID Concurrency Control & Row Locking

To eliminate race conditions during high-frequency parallel deposit requests at a single station:

- Locker slot allocations utilize PostgreSQL row-level locks via SQLAlchemy: `select(LockerSlot).with_for_update(skip_locked=True)`.
- This guarantees strict ACID compliance—concurrent drop-off requests will never double-book the same locker slot.

### 3. Dynamic Parcel Sizing & Allocation Fallback Engine

When allocating a slot for a package (Small, Medium, or Large):

- The system attempts to assign an exact size match first.
- If exact matches are occupied or in maintenance, it automatically falls back to larger available slots (`SMALL -> MEDIUM -> LARGE`).
- If no suitable slots are available, a structured `503 Service Unavailable` (`LockerFullException`) error is returned.

### 4. Tiered Storage Pricing Engine

Storage pricing is computed based on elapsed calendar days (ceiling of total hours / 24):

- **Day 1**: Free / Prepaid (RM 0.00)
- **Days 2 – 5 (Tier 1)**: RM 10.00 / day
- **Days 6 – 10 (Tier 2)**: RM 20.00 / day
- **Days 11+ (Tier 3)**: RM 30.00 / day

### 5. Deferred SMS Notification Flow

To reflect real-world hardware flows:

1. When a courier or P2P deposit request is initiated, the slot door unlocks, but **no SMS is sent immediately**.
2. The user places the parcel in the locker cavity and closes the door (`/api/allocations/deposit-confirm`).
3. **Only upon door closure confirmation**, the 6-digit secure pickup PIN SMS notification is dispatched to the recipient's phone.

### 6. Deposit Cancellation State Machine

If a courier or storer decides to cancel the drop-off while the locker door is open:

- The user clicks **"❌ Cancel Deposit"** (`/api/allocations/deposit-cancel`).
- The system instantly aborts the pending allocation, reverts the slot status back to **`AVAILABLE`**, and dispatches **zero SMS alerts**.

### 7. Alembic Automated Migration & Data Seeding

Database schema creation and initial seeding are fully automated via Alembic migrations on startup (`alembic upgrade head` in container entrypoint):

- **Seeded Malaysian Stations**: _Mid Valley Megamall Hub_, _Sunway Pyramid Station_, _KL Sentral Station_.
- **Seeded Slots**: 18 locker slots across Small, Medium, and Large dimensions.
- **Seeded Engineer Credentials**: Default maintenance engineer (`admin_engineer` / `admin123`).

### 8. Shopee Light Theme & Malaysian Localization

- **Visual Palette**: Shopee Orange (`#EE4D2D`), coral accents, clean light canvas (`#F5F5F7`), and white cards.
- **Localization**: Ringgit Malaysia (`RM`) currency, Malaysian mobile prefixes (`+60`), and default couriers (_Shopee Xpress SPX_, _Pos Laju_, _J&T Express_, _Ninja Van_).

---

## 🧪 Testing & Database Isolation

Automated test suites run against a dedicated, isolated test database (`smart_locker_test`), preventing tests from modifying or wiping production data.

### Run Local Pytest Suite

```bash
cd backend
uv run pytest
```

### Test Coverage Highlights

- **Unit Tests (`tests/unit/`)**: Pure unit testing of fee tiers, calendar day ceil calculations, and SHA-256 PIN hashing.
- **Integration & API Tests (`tests/`)**: End-to-end testing of dynamic deposits, deferred SMS confirmation, deposit cancellation, concurrency locking, and recipient retrievals.

```bash
collected 28 items

tests/test_api.py ..                                                     [  7%]
tests/test_concurrency.py .                                              [ 10%]
tests/test_courier_flow.py ...                                           [ 21%]
tests/test_notifications.py ..                                           [ 28%]
tests/test_p2p_flow.py ...                                               [ 39%]
tests/test_pricing.py ...                                                [ 50%]
tests/test_retrieval_flow.py ....                                        [ 64%]
tests/test_setup_engineer.py ...                                         [ 75%]
tests/unit/test_hashing_unit.py ..                                       [ 82%]
tests/unit/test_pricing_unit.py .....                                    [100%]

============================== 28 passed in 5.97s ==============================
```

---

## 💡 Design Trade-offs & Scope Considerations

While the following architectural features are good to have for enterprise production, they were intentionally dropped for this project scope to keep the codebase clean, lightweight, direct, and easy to run without unnecessary third-party dependencies or configuration overhead:

- **React Hook Form (RHF) + Zod**: Great for complex multi-step enterprise forms, but dropped in favor of standard controlled React component state (`useState`) to avoid extra package dependencies and keep the interactive simulator simple.
- **WebSockets / Server-Sent Events (SSE)**: Excellent for production real-time streaming, but dropped in favor of lightweight 2-3s interval polling to eliminate WebSocket connection state overhead and simplify local/Docker deployment.
- **Production SMS Gateway (Twilio / AWS SNS)**: Essential for actual cellular delivery, but dropped in favor of an in-memory notification log enqueuer (`InMemoryNotificationSender`) so reviewers can inspect simulated SMS output directly on the virtual phone UI without requiring paid third-party API keys.
- **IoT Hardware Webhooks (MQTT)**: Great for physical locker hardware integrations, but dropped in favor of interactive browser simulation buttons (`Close Door & Dispatch SMS`) so the complete door sensor flow can be tested in any browser without micro-controllers.
- **JWT / OAuth2 Authorization Servers**: Good to have for multi-tenant auth, but dropped for direct SHA-256 password hashing to keep engineer authentication clean and focused.

### ⚠️ Uncovered Hardware & Edge Case Scenarios

In physical production deployments, hardware sensors and automated operational policies resolve real-world edge cases not covered in this software prototype scope:

- **Premature Door Closure without Parcel Removal**: If a recipient opens the locker door, forgets or leaves their package inside, and accidentally closes the door:
  - *Current Prototype Behavior*: The system detects door closure (`/api/allocations/retrieve-complete`) and completes the allocation, resetting slot status to `AVAILABLE`.
  - *Production Solution*: Internal weight/optical break-beam sensors inside the locker cavity verify parcel removal before freeing the slot, accompanied by a 60-second "Re-open Door" grace period button on the kiosk terminal.
- **Overdue / Abandoned Package Auto-Eviction**: If a recipient leaves a package unclaimed for an extended period (e.g. >30 days):
  - *Current Prototype Behavior*: Tiered storage fees accrue daily without an automatic eviction cap.
  - *Production Solution*: Scheduled background worker jobs auto-flag allocations as `ABANDONED` after a threshold (e.g. 14 or 30 days) and generate engineer maintenance tickets to clear the slot.
- **Volumetric Parcel Sizing Mismatch**: If a courier selects a Large slot for a Small package or attempts to force an oversized parcel:
  - *Current Prototype Behavior*: Allocates based directly on courier form input.
  - *Production Solution*: 3D optical light-curtains inside each locker frame measure parcel dimensions automatically upon door closure to verify physical package size.

---

## 🔑 Default Credentials

| Role                     | Username         | Password   | Engineer Code |
| :----------------------- | :--------------- | :--------- | :------------ |
| **Maintenance Engineer** | `admin_engineer` | `admin123` | `ENG-MY01`    |
