"""Legacy command name retained for compatibility; this no longer resets data.

Use ``seed_demo_data.py`` to add any missing demo fixtures. Existing users,
facilities, requests, inventory, and history are left in place.
"""

from __future__ import annotations

import asyncio

from scripts.seed_demo_data import seed_data


async def reset() -> None:
    await seed_data()


if __name__ == "__main__":
    asyncio.run(reset())
