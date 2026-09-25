# backend/scripts/reset_to_demo.py
# LifeLink AI — Database Reset to Strict 4-Account Demo State
# Purges any stray accounts and resets to the strict 4-account configuration with active requests.

from __future__ import annotations

import asyncio
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.seed_strict_4 import seed_strict_accounts


async def reset():
    await seed_strict_accounts()


if __name__ == "__main__":
    asyncio.run(reset())
