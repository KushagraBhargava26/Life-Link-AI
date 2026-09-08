import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from sqlalchemy import text
from app.database import get_engine

async def main():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS blood_bank_emergency_responses CASCADE;'))
        await conn.execute(text('''
            CREATE TABLE blood_bank_emergency_responses (
                id UUID PRIMARY KEY,
                emergency_request_id UUID NOT NULL REFERENCES emergency_requests(id) ON DELETE CASCADE,
                blood_bank_id UUID NOT NULL REFERENCES blood_banks(id) ON DELETE CASCADE,
                blood_type VARCHAR(10) NOT NULL,
                units_requested INTEGER NOT NULL DEFAULT 1,
                units_committed INTEGER NOT NULL DEFAULT 0,
                status VARCHAR(30) NOT NULL DEFAULT 'ACCEPTED',
                message TEXT,
                responded_by UUID REFERENCES users(id) ON DELETE SET NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_bb_response_req_bank UNIQUE (emergency_request_id, blood_bank_id)
            );
        '''))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_bb_emergency_responses_req_id ON blood_bank_emergency_responses (emergency_request_id);'))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_bb_emergency_responses_bank_id ON blood_bank_emergency_responses (blood_bank_id);'))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS ix_bb_emergency_responses_status ON blood_bank_emergency_responses (status);'))
        print('Table blood_bank_emergency_responses successfully aligned with ORM model!')

if __name__ == '__main__':
    asyncio.run(main())
