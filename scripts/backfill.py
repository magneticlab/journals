#!/usr/bin/env python3
"""
Backfill — generate journals for a date range.
Usage: python3 backfill.py YYYY-MM-DD YYYY-MM-DD
       python3 backfill.py 30  (last 30 days)
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def main():
    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        # Last N days
        days = int(sys.argv[1])
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days - 1)
    elif len(sys.argv) == 3:
        start_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        end_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
    else:
        print("Usage: python3 backfill.py YYYY-MM-DD YYYY-MM-DD")
        print("       python3 backfill.py 30  (last 30 days)")
        sys.exit(1)

    current = start_date
    generated = 0
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "generate_work_journal.py"), date_str],
            check=True,
        )
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "generate_daily_journal.py"), date_str],
            check=True,
        )
        generated += 1
        current += timedelta(days=1)

    # Rebuild indexes
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "build_index.py")],
        check=True,
    )

    print(f"\nBackfilled {generated} days. Indexes rebuilt.")


if __name__ == "__main__":
    main()
