#!/usr/bin/env python3
"""
Daily Journal Generator — Laptop Activity
Summarizes daily activity from shell history, git logs, and file system changes.
"""

import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

REPOS_DIR = Path.home() / "Documents" / "GitHub"
OUTPUT_DIR = Path(__file__).parent.parent / "daily" / "entries"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_shell_history_for_date(target_date: str) -> list[dict]:
    """Extract shell commands from zsh history for a given date.

    Supports both extended format (: timestamp:0;command) and macOS
    session-based history (~/.zsh_sessions/*.history) where we use
    the session file's modification date as a rough timestamp.
    """
    entries = []
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_end = target_dt + timedelta(days=1)

    # Try extended history format first
    history_file = Path.home() / ".zsh_history"
    if history_file.exists():
        try:
            with open(history_file, "rb") as f:
                for raw_line in f:
                    try:
                        line = raw_line.decode("utf-8", errors="replace").strip()
                    except UnicodeDecodeError:
                        continue

                    if line.startswith(": "):
                        parts = line[2:].split(";", 1)
                        if len(parts) == 2:
                            try:
                                ts_part = parts[0].split(":")[0]
                                ts = int(ts_part)
                                cmd_time = datetime.fromtimestamp(ts)
                                if target_dt <= cmd_time < target_end:
                                    cmd = parts[1].strip()
                                    entries.append({
                                        "time": cmd_time.strftime("%H:%M"),
                                        "command": cmd,
                                    })
                            except (ValueError, OSError):
                                continue
        except PermissionError:
            pass

    # Also check macOS session-based history files
    sessions_dir = Path.home() / ".zsh_sessions"
    if sessions_dir.exists():
        for hist_file in sessions_dir.glob("*.history"):
            try:
                mtime = datetime.fromtimestamp(hist_file.stat().st_mtime)
                # Only process session files modified on the target date
                if not (target_dt <= mtime < target_end):
                    continue
                time_str = mtime.strftime("%H:%M")
                with open(hist_file, "rb") as f:
                    for raw_line in f:
                        try:
                            line = raw_line.decode("utf-8", errors="replace").strip()
                        except UnicodeDecodeError:
                            continue
                        if line and not line.startswith(": "):
                            entries.append({
                                "time": time_str,
                                "command": line,
                            })
            except (PermissionError, OSError):
                continue

    # Deduplicate
    seen = set()
    unique = []
    for e in entries:
        key = e["command"]
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


def get_git_activity_all_repos(target_date: str) -> dict[str, list[dict]]:
    """Get git commits across all repos for a given date."""
    activity = {}

    if not REPOS_DIR.exists():
        return activity

    for repo_dir in sorted(REPOS_DIR.iterdir()):
        if not repo_dir.is_dir():
            continue
        git_dir = repo_dir / ".git"
        if not git_dir.exists():
            continue

        repo_name = repo_dir.name
        try:
            result = subprocess.run(
                [
                    "git", "log",
                    f"--after={target_date} 00:00:00",
                    f"--before={target_date} 23:59:59",
                    "--all",
                    "--format=%H|%an|%s|%ai",
                    "--no-merges",
                ],
                cwd=str(repo_dir),
                capture_output=True,
                text=True,
                timeout=10,
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0][:7],
                        "author": parts[1],
                        "message": parts[2],
                        "time": parts[3],
                    })

            if commits:
                activity[repo_name] = commits
        except (subprocess.TimeoutExpired, Exception):
            continue

    return activity


def get_recently_modified_files(target_date: str) -> list[str]:
    """Find files modified on the target date in common working directories."""
    modified = []
    search_dirs = [
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home() / "Downloads",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        try:
            result = subprocess.run(
                [
                    "find", str(search_dir),
                    "-maxdepth", "3",
                    "-type", "f",
                    "-newermt", f"{target_date} 00:00:00",
                    "!", "-newermt", f"{target_date} 23:59:59",
                    "-not", "-path", "*/node_modules/*",
                    "-not", "-path", "*/.git/*",
                    "-not", "-path", "*/.claude/*",
                    "-not", "-name", ".DS_Store",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    # Make path relative to home
                    rel = line.replace(str(Path.home()), "~")
                    modified.append(rel)
        except (subprocess.TimeoutExpired, Exception):
            continue

    return sorted(modified)[:50]  # Cap at 50


def categorize_commands(commands: list[dict]) -> dict[str, list[dict]]:
    """Categorize shell commands into groups."""
    categories = defaultdict(list)

    for cmd in commands:
        c = cmd["command"]
        if c.startswith("git "):
            categories["Git"].append(cmd)
        elif c.startswith("npm ") or c.startswith("yarn ") or c.startswith("pnpm "):
            categories["Package Management"].append(cmd)
        elif c.startswith("cd "):
            categories["Navigation"].append(cmd)
        elif c.startswith("claude") or c.startswith("cc "):
            categories["Claude Code"].append(cmd)
        elif c.startswith("python") or c.startswith("pip ") or c.startswith("python3"):
            categories["Python"].append(cmd)
        elif c.startswith("brew "):
            categories["Homebrew"].append(cmd)
        elif c.startswith("docker") or c.startswith("docker-compose"):
            categories["Docker"].append(cmd)
        elif c.startswith("ssh ") or c.startswith("scp "):
            categories["Remote"].append(cmd)
        elif c.startswith("curl ") or c.startswith("wget "):
            categories["HTTP"].append(cmd)
        elif any(c.startswith(s) for s in ["ls", "cat", "head", "tail", "grep", "find", "wc"]):
            categories["File Inspection"].append(cmd)
        elif any(c.startswith(s) for s in ["mkdir", "rm ", "mv ", "cp ", "touch"]):
            categories["File Operations"].append(cmd)
        elif c.startswith("gh "):
            categories["GitHub CLI"].append(cmd)
        else:
            categories["Other"].append(cmd)

    return dict(categories)


def generate_report(target_date: str) -> str:
    """Generate the daily laptop activity journal."""
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    day_name = WEEKDAYS[dt.weekday()]

    shell_history = get_shell_history_for_date(target_date)
    git_activity = get_git_activity_all_repos(target_date)
    modified_files = get_recently_modified_files(target_date)

    total_commits = sum(len(v) for v in git_activity.values())

    lines = []
    lines.append(f"# Daily Journal — {day_name}, {dt.strftime('%B %d, %Y')}")
    lines.append("")

    # Narrative lead
    lines.append(f"> {len(shell_history)} terminal commands, {total_commits} git commits across {len(git_activity)} repos, {len(modified_files)} files modified.")
    lines.append("")

    # Shell Activity Summary
    if shell_history:
        categories = categorize_commands(shell_history)
        lines.append("## Terminal Activity")
        lines.append("")
        lines.append("| Category | Commands |")
        lines.append("|----------|----------|")
        for cat, cmds in sorted(categories.items(), key=lambda x: -len(x[1])):
            lines.append(f"| {cat} | {len(cmds)} |")
        lines.append("")

        # Time distribution
        hours = defaultdict(int)
        for cmd in shell_history:
            h = cmd["time"].split(":")[0]
            hours[h] += 1

        lines.append("### Activity by Hour")
        lines.append("")
        for hour in sorted(hours.keys()):
            bar = "█" * min(hours[hour], 40)
            lines.append(f"- `{hour}:00` {bar} ({hours[hour]})")
        lines.append("")

        # Notable commands (skip trivial ones)
        notable = [
            cmd for cmd in shell_history
            if not cmd["command"].startswith(("ls", "cd ", "clear", "pwd"))
            and len(cmd["command"]) > 3
        ]
        if notable:
            lines.append("### Notable Commands")
            lines.append("")
            seen = set()
            for cmd in notable[:40]:
                # Deduplicate exact same commands
                c = cmd["command"][:120]
                if c not in seen:
                    seen.add(c)
                    lines.append(f"- `{cmd['time']}` `{c}`")
            lines.append("")

    # Git Activity
    if git_activity:
        lines.append("## Git Activity")
        lines.append("")
        lines.append("| Repo | Commits |")
        lines.append("|------|---------|")
        for repo_name, commits in sorted(git_activity.items()):
            lines.append(f"| {repo_name} | {len(commits)} |")
        lines.append("")

        for repo_name, commits in sorted(git_activity.items()):
            lines.append(f"### {repo_name}")
            lines.append("")
            for c in commits:
                time_str = c["time"].split(" ")[1][:5] if " " in c["time"] else ""
                lines.append(f"- `{c['hash']}` {time_str} — {c['message']} ({c['author']})")
            lines.append("")

    # Modified Files
    if modified_files:
        lines.append("## Files Modified")
        lines.append("")

        # Group by directory
        by_dir = defaultdict(list)
        for f in modified_files:
            parts = f.split("/")
            if len(parts) >= 3:
                dir_key = "/".join(parts[:3])
            else:
                dir_key = "/".join(parts[:-1]) or "~"
            by_dir[dir_key].append(f)

        for dir_key, files in sorted(by_dir.items()):
            lines.append(f"**{dir_key}/** ({len(files)} files)")
            for f in files[:10]:
                lines.append(f"- `{f}`")
            if len(files) > 10:
                lines.append(f"- *...and {len(files) - 10} more*")
            lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} from shell history, git logs, and file system.*")

    return "\n".join(lines)


def main():
    import sys

    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")

    report = generate_report(target_date)
    output_file = OUTPUT_DIR / f"{target_date}.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report)
    print(f"Daily journal written to {output_file}")


if __name__ == "__main__":
    main()
