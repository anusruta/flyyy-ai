#!/usr/bin/env python3
"""
FLYY.AI Demo Runner
===================
Runs all three demo applications in sequence to populate
the governance dashboard with realistic data.

Usage:
    python run_demo.py
    python run_demo.py --skip-wait     # don't wait between demos
"""

import asyncio
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from customer_support import run_customer_support_demo
from hr_assistant import run_hr_assistant_demo
from support_agent import run_support_agent_demo


async def main(skip_wait: bool = False):
    print("\n" + "█" * 60)
    print("  FLYY.AI — Full Demo Runner")
    print("  AI Governance & Observability Platform")
    print("█" * 60)
    print()
    print("  This will populate the dashboard with:")
    print("  1. Customer Support AI — 15 interactions (7 with PII)")
    print("  2. HR Assistant        — 12 interactions (0 PII)")
    print("  3. Support Agent       — 5 runs (2 governance violations)")
    print()

    # ── Demo 1: Customer Support AI ──────────────────────────────────────────
    print("  Starting Demo 1/3: Customer Support AI...")
    await run_customer_support_demo()

    if not skip_wait:
        await asyncio.sleep(1)

    # ── Demo 2: HR Assistant ──────────────────────────────────────────────────
    print("  Starting Demo 2/3: HR Assistant...")
    await run_hr_assistant_demo()

    if not skip_wait:
        await asyncio.sleep(1)

    # ── Demo 3: Support Agent (with violations) ───────────────────────────────
    print("  Starting Demo 3/3: Customer Support Agent...")
    await run_support_agent_demo()

    print("\n" + "█" * 60)
    print("  ✅ All demos complete!")
    print()
    print("  Open the dashboard: http://localhost:3000")
    print()
    print("  Key things to check:")
    print("  • Overview    → PII incidents and violation counts")
    print("  • AI Assets   → 3 monitored assets")
    print("  • Prompts     → Sanitized prompts, PII badges")
    print("  • Agent Runs  → 2 runs marked ⚠ VIOLATION")
    print("  • Governance  → Policy violation details")
    print("█" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FLYY.AI Demo Runner")
    parser.add_argument("--skip-wait", action="store_true", help="Skip delays between demos")
    args = parser.parse_args()
    asyncio.run(main(skip_wait=args.skip_wait))
