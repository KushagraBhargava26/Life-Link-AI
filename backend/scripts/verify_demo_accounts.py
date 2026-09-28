"""Read-only verification of the demo credentials advertised by the frontend."""

from __future__ import annotations

import asyncio

from scripts.seed_demo_data import verify_demo_accounts


if __name__ == "__main__":
    asyncio.run(verify_demo_accounts())
