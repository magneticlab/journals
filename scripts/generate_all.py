#!/usr/bin/env python3
"""
Master script — generates all journal types for a given date and rebuilds indexes.
Usage: python3 generate_all.py [YYYY-MM-DD]

After generating, optionally auto-commits and pushes (controlled by journals.config.js).
Pass --no-push to skip the git step.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT = SCRIPTS_DIR.parent

sys.path.insert(0, str(SCRIPTS_DIR))
from config import get as get_config


def run_script(name, *args):
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / name), *args],
        check=True,
    )


def git_publish(target_date):
    """Stage entries, commit if there are changes, push to origin/dev."""
    paths = [
        "app/public/entries",
        "app/public/manifest.json",
        "daily/index.html",
        "work/index.html",
    ]

    add = subprocess.run(
        ["git", "add", *paths],
        cwd=REPO_ROOT,
    )
    if add.returncode != 0:
        print("git add failed — skipping publish", file=sys.stderr)
        return

    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_ROOT,
    )
    if diff.returncode == 0:
        print("No new entries to publish.")
        return

    msg = f"chore: auto-generate journal entries for {target_date}"
    commit = subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=REPO_ROOT,
    )
    if commit.returncode != 0:
        print("git commit failed — skipping push", file=sys.stderr)
        return

    push = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        cwd=REPO_ROOT,
    )
    if push.returncode != 0:
        print("git push failed — entries committed locally only", file=sys.stderr)
        return

    print(f"Published entries for {target_date} to origin.")


def main():
    args = [a for a in sys.argv[1:] if a != "--no-push"]
    no_push = "--no-push" in sys.argv
    target_date = args[0] if args else datetime.now().strftime("%Y-%m-%d")

    # Pull latest entries from remote (other machines may have pushed)
    pull = subprocess.run(
        ["git", "pull", "--rebase", "--autostash", "origin", "main"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    if pull.returncode == 0 and "Already up to date" not in pull.stdout:
        print(f"Pulled latest entries from remote.")

    print(f"Generating journals for {target_date}...")
    print()

    run_script("generate_work_journal.py", target_date)
    run_script("generate_daily_journal.py", target_date)
    # Narrative is sourced from ~/.claude/.../memory/journal/*.md and may not exist
    # for every date — the generator silently no-ops when no source files match.
    run_script("generate_narrative.py", target_date)
    run_script("build_index.py")
    run_script("build_manifest.py")

    print()

    cfg = get_config()
    auto_push = cfg.get("git", {}).get("autoPush", False)

    if no_push or not auto_push:
        if no_push:
            print("Done (--no-push set). Open http://localhost:5173/")
        else:
            print("Done (autoPush disabled). Open http://localhost:5173/")
        return

    git_publish(target_date)
    print("Done. Open http://localhost:5173/")


if __name__ == "__main__":
    main()
