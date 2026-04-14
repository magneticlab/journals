#!/usr/bin/env python3
"""
Work Journal Generator — Claude Code Sessions
Reads ~/.claude/history.jsonl + git logs across repos to produce a daily work report.
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

HISTORY_FILE = Path.home() / ".claude" / "history.jsonl"
REPOS_DIR = Path.home() / "Documents" / "GitHub"
OUTPUT_DIR = Path(__file__).parent.parent / "work" / "entries"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_history_for_date(target_date: str) -> list[dict]:
    """Load all Claude Code history entries for a given date (YYYY-MM-DD)."""
    entries = []
    target_start = datetime.strptime(target_date, "%Y-%m-%d")
    target_end = target_start + timedelta(days=1)
    start_ts = target_start.timestamp() * 1000
    end_ts = target_end.timestamp() * 1000

    if not HISTORY_FILE.exists():
        return entries

    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("timestamp", 0)
                if start_ts <= ts < end_ts:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue

    return sorted(entries, key=lambda e: e.get("timestamp", 0))


def get_git_activity(target_date: str) -> dict[str, list[dict]]:
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

            # Get diff stats for the day
            stat_result = subprocess.run(
                [
                    "git", "log",
                    f"--after={target_date} 00:00:00",
                    f"--before={target_date} 23:59:59",
                    "--all",
                    "--stat",
                    "--format=",
                    "--no-merges",
                ],
                cwd=str(repo_dir),
                capture_output=True,
                text=True,
                timeout=10,
            )
            stat_summary = ""
            for line in stat_result.stdout.strip().split("\n"):
                if "files changed" in line or "file changed" in line:
                    stat_summary = line.strip()

            if commits:
                activity[repo_name] = {
                    "commits": commits,
                    "stat_summary": stat_summary,
                }
        except (subprocess.TimeoutExpired, Exception):
            continue

    return activity


def group_sessions(entries: list[dict]) -> dict[str, list[dict]]:
    """Group history entries by session ID."""
    sessions = defaultdict(list)
    for entry in entries:
        sid = entry.get("sessionId", "unknown")
        sessions[sid].append(entry)
    return dict(sessions)


def extract_topics(entries: list[dict]) -> list[str]:
    """Extract unique topics/themes from message displays."""
    topics = []
    for entry in entries:
        display = entry.get("display", "")
        if display and not display.startswith("/") and not display.startswith("[Image"):
            # Clean up the display text
            text = display[:120].strip()
            if text:
                topics.append(text)
    return topics


def get_project_label(project_path: str) -> str:
    """Convert a project path to a readable label."""
    if not project_path:
        return "unknown"
    parts = project_path.rstrip("/").split("/")
    # Return the last meaningful directory name
    return parts[-1] if parts else "unknown"


def generate_report(target_date: str) -> str:
    """Generate the full work journal entry for a date."""
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    day_name = WEEKDAYS[dt.weekday()]

    entries = load_history_for_date(target_date)
    git_activity = get_git_activity(target_date)
    sessions = group_sessions(entries)

    if not entries and not git_activity:
        return f"# Work Journal — {day_name}, {dt.strftime('%B %d, %Y')}\n\n> No Claude Code sessions or git activity recorded for this day.\n"

    # Build session summary
    projects_used = defaultdict(int)
    for entry in entries:
        proj = get_project_label(entry.get("project", ""))
        projects_used[proj] += 1

    total_messages = len(entries)
    total_sessions = len(sessions)

    # Time range
    if entries:
        first_ts = entries[0].get("timestamp", 0) / 1000
        last_ts = entries[-1].get("timestamp", 0) / 1000
        first_time = datetime.fromtimestamp(first_ts).strftime("%H:%M")
        last_time = datetime.fromtimestamp(last_ts).strftime("%H:%M")
        time_range = f"{first_time}–{last_time}"
    else:
        time_range = "N/A"

    # Total commits across all repos
    total_commits = sum(len(v["commits"]) for v in git_activity.values())

    lines = []
    lines.append(f"# Work Journal — {day_name}, {dt.strftime('%B %d, %Y')}")
    lines.append("")

    # Narrative lead
    project_list = ", ".join(sorted(projects_used.keys()))
    lines.append(f"> {total_sessions} Claude session(s), {total_messages} messages across {time_range}. Projects touched: {project_list}. {total_commits} git commit(s) across {len(git_activity)} repo(s).")
    lines.append("")

    # Claude Sessions
    lines.append("## Claude Sessions")
    lines.append("")
    lines.append("| # | Project | Messages | Time Range |")
    lines.append("|---|---------|----------|------------|")

    for i, (sid, sess_entries) in enumerate(sessions.items(), 1):
        proj = get_project_label(sess_entries[0].get("project", ""))
        msg_count = len(sess_entries)
        s_first = datetime.fromtimestamp(sess_entries[0]["timestamp"] / 1000).strftime("%H:%M")
        s_last = datetime.fromtimestamp(sess_entries[-1]["timestamp"] / 1000).strftime("%H:%M")
        lines.append(f"| {i} | {proj} | {msg_count} | {s_first}–{s_last} |")

    lines.append("")

    # Topics / Prompts per session
    lines.append("## Session Topics")
    lines.append("")

    for i, (sid, sess_entries) in enumerate(sessions.items(), 1):
        proj = get_project_label(sess_entries[0].get("project", ""))
        lines.append(f"### Session {i} — {proj}")
        lines.append("")

        topics = extract_topics(sess_entries)
        if topics:
            for topic in topics[:15]:  # Cap at 15 per session
                lines.append(f"- {topic}")
            if len(topics) > 15:
                lines.append(f"- *...and {len(topics) - 15} more*")
        else:
            lines.append("- *(No text prompts recorded — may have been image/paste-only)*")
        lines.append("")

    # Git Activity
    if git_activity:
        lines.append("## Git Activity")
        lines.append("")
        lines.append("| Repo | Commits | Summary |")
        lines.append("|------|---------|---------|")

        for repo_name, data in sorted(git_activity.items()):
            commit_count = len(data["commits"])
            stat = data.get("stat_summary", "")
            lines.append(f"| {repo_name} | {commit_count} | {stat} |")

        lines.append("")

        # Commit details
        for repo_name, data in sorted(git_activity.items()):
            lines.append(f"### {repo_name}")
            lines.append("")
            for c in data["commits"]:
                time_str = c["time"].split(" ")[1][:5] if " " in c["time"] else ""
                lines.append(f"- `{c['hash']}` {time_str} — {c['message']} ({c['author']})")
            lines.append("")

    # Footer
    lines.append("---")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} from `~/.claude/history.jsonl` and git logs.*")

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
    print(f"Work journal written to {output_file}")


if __name__ == "__main__":
    main()
