#!/usr/bin/env python3
"""
Master script — generates both journals for a given date and rebuilds indexes.
Usage: python3 generate_all.py [YYYY-MM-DD]
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")

    print(f"Generating journals for {target_date}...")
    print()

    # Generate work journal
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_work_journal.py"), target_date],
        check=True,
    )

    # Generate daily journal
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "generate_daily_journal.py"), target_date],
        check=True,
    )

    # Rebuild indexes
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "build_index.py")],
        check=True,
    )

    # Rebuild app manifest
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "build_manifest.py")],
        check=True,
    )

    print()
    print("Done. Open http://localhost:3010/")


if __name__ == "__main__":
    main()
