"""seed_initial_data

Revision ID: 55d0f91e0096
Revises: 7825fb7598a6
Create Date: 2026-07-22 07:06:08.423644

"""
import uuid
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55d0f91e0096'
down_revision: Union[str, Sequence[str], None] = '7825fb7598a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema and seed initial Malaysian locker stations, slots, and engineer."""
    # 1. Seed Default Engineer (admin_engineer / admin123)
    engineers_table = sa.table(
        'engineers',
        sa.column('id', sa.UUID),
        sa.column('username', sa.String),
        sa.column('password_hash', sa.String),
        sa.column('engineer_code', sa.String)
    )
    op.bulk_insert(engineers_table, [{
        'id': 'a1b2c3d4-e5f6-4a5b-8c7d-9e0f1a2b3c4d',
        'username': 'admin_engineer',
        'password_hash': '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        'engineer_code': 'ENG-MY01'
    }])

    # 2. Seed Default Malaysian Locker Stations
    stations_table = sa.table(
        'locker_stations',
        sa.column('id', sa.UUID),
        sa.column('name', sa.String),
        sa.column('address', sa.String)
    )
    stations_data = [
        {
            'id': 'ff7c5563-28e4-4cdf-a960-b6427a8f989d',
            'name': 'Mid Valley Megamall Hub',
            'address': 'Mid Valley Megamall, Lingkaran Syed Putra, Mid Valley City, 59200 Kuala Lumpur'
        },
        {
            'id': '5bd73ba6-907c-4f37-b953-3a24fdb5d93a',
            'name': 'Sunway Pyramid Station',
            'address': 'Sunway Pyramid, 3, Jalan PJS 11/15, Bandar Sunway, 47500 Subang Jaya'
        },
        {
            'id': '8534dda3-7b14-47db-ba18-766e2f6f1b6d',
            'name': 'KL Sentral Station',
            'address': 'Stesen Sentral Kuala Lumpur, 50470 Kuala Lumpur'
        }
    ]
    op.bulk_insert(stations_table, stations_data)

    # 3. Seed Default Locker Slots for each station
    slots_table = sa.table(
        'locker_slots',
        sa.column('id', sa.UUID),
        sa.column('station_id', sa.UUID),
        sa.column('slot_code', sa.String),
        sa.column('size', sa.String),
        sa.column('status', sa.String)
    )
    
    slots_data = []
    slot_defs = [
        ("S-01", "SMALL"),
        ("S-02", "SMALL"),
        ("S-03", "SMALL"),
        ("M-01", "MEDIUM"),
        ("M-02", "MEDIUM"),
        ("L-01", "LARGE")
    ]
    for station in stations_data:
        for code, size in slot_defs:
            slots_data.append({
                'id': str(uuid.uuid4()),
                'station_id': station['id'],
                'slot_code': code,
                'size': size,
                'status': 'AVAILABLE'
            })
            
    op.bulk_insert(slots_table, slots_data)


def downgrade() -> None:
    """Downgrade schema and remove seeded data."""
    op.execute("DELETE FROM locker_slots WHERE slot_code IN ('S-01', 'S-02', 'S-03', 'M-01', 'M-02', 'L-01')")
    op.execute("DELETE FROM locker_stations WHERE name IN ('Mid Valley Megamall Hub', 'Sunway Pyramid Station', 'KL Sentral Station')")
    op.execute("DELETE FROM engineers WHERE username = 'admin_engineer'")
