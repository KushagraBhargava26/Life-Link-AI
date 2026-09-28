"""Legacy seed command; this now adds missing demo fixtures without purging data."""

from __future__ import annotations

import asyncio

from scripts.seed_demo_data import seed_data


async def seed_strict_accounts() -> None:
    """Backward-compatible function name for the non-destructive demo seed."""
    await seed_data()


if __name__ == "__main__":
    asyncio.run(seed_strict_accounts())
