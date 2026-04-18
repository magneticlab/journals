#!/usr/bin/env python3
"""
Daily Journal Generator — Laptop Activity
Outputs structured JSON for the Vue app.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

from config import get as get_config

_cfg = get_config()
REPOS_DIR = Path.home() / _cfg["sources"]["reposDir"]
MACHINE_ID = _cfg.get("machineId", "default")
OUTPUT_DIR = Path(__file__).parent.parent / "daily" / "entries"
APP_PUBLIC = Path(__file__).parent.parent / "app" / "public" / "entries" / "daily"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_shell_history_for_date(target_date: str) -> list[dict]:
    entries = []
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    target_end = target_dt + timedelta(days=1)

    # Extended history format
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
                                ts = int(parts[0].split(":")[0])
                                cmd_time = datetime.fromtimestamp(ts)
                                if target_dt <= cmd_time < target_end:
                                    entries.append({"time": cmd_time.strftime("%H:%M"), "command": parts[1].strip()})
                            except (ValueError, OSError):
                                continue
        except PermissionError:
            pass

    # macOS session-based history
    sessions_dir = Path.home() / ".zsh_sessions"
    if sessions_dir.exists():
        for hist_file in sessions_dir.glob("*.history"):
            try:
                mtime = datetime.fromtimestamp(hist_file.stat().st_mtime)
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
                            entries.append({"time": time_str, "command": line})
            except (PermissionError, OSError):
                continue

    seen = set()
    unique = []
    for e in entries:
        if e["command"] not in seen:
            seen.add(e["command"])
            unique.append(e)
    return unique


def get_git_activity(target_date: str) -> list[dict]:
    activity = []
    if not REPOS_DIR.exists():
        return activity

    for repo_dir in sorted(REPOS_DIR.iterdir()):
        if not repo_dir.is_dir() or not (repo_dir / ".git").exists():
            continue
        repo_name = repo_dir.name
        try:
            result = subprocess.run(
                ["git", "log", f"--after={target_date} 00:00:00",
                 f"--before={target_date} 23:59:59", "--all",
                 "--format=%H|%an|%s|%ai", "--no-merges"],
                cwd=str(repo_dir), capture_output=True, text=True, timeout=10,
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
                        "time": parts[3].split(" ")[1][:5] if " " in parts[3] else "",
                    })
            if commits:
                activity.append({"repo": repo_name, "commits": commits})
        except (subprocess.TimeoutExpired, Exception):
            continue
    return activity


def get_modified_files(target_date: str) -> list[str]:
    modified = []
    search_dirs = [Path.home() / "Documents", Path.home() / "Desktop", Path.home() / "Downloads"]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        try:
            result = subprocess.run(
                ["find", str(search_dir), "-maxdepth", "3", "-type", "f",
                 "-newermt", f"{target_date} 00:00:00", "!", "-newermt", f"{target_date} 23:59:59",
                 "-not", "-path", "*/node_modules/*", "-not", "-path", "*/.git/*",
                 "-not", "-path", "*/.claude/*", "-not", "-name", ".DS_Store"],
                capture_output=True, text=True, timeout=30,
            )
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    modified.append(line.replace(str(Path.home()), "~"))
        except (subprocess.TimeoutExpired, Exception):
            continue
    return sorted(modified)[:50]


def categorize_commands(commands: list[dict]) -> dict[str, int]:
    cats = defaultdict(int)
    for cmd in commands:
        c = cmd["command"]
        if c.startswith("git "):
            cats["Git"] += 1
        elif any(c.startswith(s) for s in ["npm ", "yarn ", "pnpm "]):
            cats["Package Management"] += 1
        elif c.startswith("cd "):
            cats["Navigation"] += 1
        elif any(c.startswith(s) for s in ["claude", "cc "]):
            cats["Claude Code"] += 1
        elif any(c.startswith(s) for s in ["python", "pip "]):
            cats["Python"] += 1
        elif c.startswith("brew "):
            cats["Homebrew"] += 1
        elif any(c.startswith(s) for s in ["docker", "docker-compose"]):
            cats["Docker"] += 1
        elif any(c.startswith(s) for s in ["ssh ", "scp "]):
            cats["Remote"] += 1
        elif c.startswith("gh "):
            cats["GitHub CLI"] += 1
        elif any(c.startswith(s) for s in ["ls", "cat", "head", "tail", "grep", "find", "wc"]):
            cats["File Inspection"] += 1
        elif any(c.startswith(s) for s in ["mkdir", "rm ", "mv ", "cp ", "touch"]):
            cats["File Operations"] += 1
        else:
            cats["Other"] += 1
    return dict(sorted(cats.items(), key=lambda x: -x[1]))


def generate_report(target_date: str) -> dict:
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    day_name = WEEKDAYS[dt.weekday()]

    shell_history = get_shell_history_for_date(target_date)
    git_activity = get_git_activity(target_date)
    modified_files = get_modified_files(target_date)

    total_commits = sum(len(r["commits"]) for r in git_activity)

    if not shell_history and not git_activity and not modified_files:
        return None

    categories = categorize_commands(shell_history) if shell_history else {}

    # Activity by hour
    hours = defaultdict(int)
    for cmd in shell_history:
        h = cmd["time"].split(":")[0]
        hours[h] += 1

    # Notable commands
    notable = []
    seen = set()
    for cmd in shell_history:
        c = cmd["command"]
        if c.startswith(("ls", "cd ", "clear", "pwd")) or len(c) <= 3:
            continue
        short = c[:120]
        if short not in seen:
            seen.add(short)
            notable.append({"time": cmd["time"], "command": short})
        if len(notable) >= 30:
            break

    # Group modified files by directory
    file_groups = defaultdict(list)
    for f in modified_files:
        parts = f.split("/")
        dir_key = "/".join(parts[:3]) if len(parts) >= 3 else "/".join(parts[:-1]) or "~"
        file_groups[dir_key].append(f)

    return {
        "date": target_date,
        "day": day_name,
        "display": dt.strftime("%B %d, %Y"),
        "generatedAt": datetime.now().isoformat(),
        "summary": f"{len(shell_history)} terminal commands, {total_commits} commits across {len(git_activity)} repos, {len(modified_files)} files modified.",
        "stats": {
            "commands": len(shell_history),
            "commits": total_commits,
            "repos": len(git_activity),
            "filesModified": len(modified_files),
        },
        "categories": categories,
        "activityByHour": dict(sorted(hours.items())),
        "notableCommands": notable,
        "gitActivity": git_activity,
        "fileGroups": {k: v[:10] for k, v in sorted(file_groups.items())},
    }


def merge_reports(existing, new_report, machine_id):
    """Merge this machine's daily report with existing data from other machines."""
    machines = existing.get("_machines", {})

    if not machines and existing.get("machineId") and existing["machineId"] != machine_id:
        machines[existing["machineId"]] = existing

    machines[machine_id] = {k: v for k, v in new_report.items() if k != "_machines"}

    if len(machines) <= 1:
        new_report["_machines"] = machines
        new_report["machineId"] = machine_id
        return new_report

    # Aggregate across machines
    all_commands = 0
    all_commits_set = set()
    all_repos = set()
    all_files = 0
    merged_git = {}
    merged_categories = defaultdict(int)
    merged_hours = defaultdict(int)
    merged_notable = []
    merged_file_groups = {}

    for mid, rpt in machines.items():
        stats = rpt.get("stats", {})
        all_commands += stats.get("commands", 0)
        all_files += stats.get("filesModified", 0)

        for repo in rpt.get("gitActivity", []):
            rname = repo["repo"]
            if rname not in merged_git:
                merged_git[rname] = {"repo": rname, "commits": []}
            seen = {c["hash"] for c in merged_git[rname]["commits"]}
            for c in repo["commits"]:
                if c["hash"] not in seen:
                    merged_git[rname]["commits"].append(c)
                    all_commits_set.add(c["hash"])
            all_repos.add(rname)

        for cat, count in rpt.get("categories", {}).items():
            merged_categories[cat] += count

        for h, count in rpt.get("activityByHour", {}).items():
            merged_hours[h] += count

        merged_notable.extend(rpt.get("notableCommands", []))

        for grp, files in rpt.get("fileGroups", {}).items():
            if grp not in merged_file_groups:
                merged_file_groups[grp] = []
            merged_file_groups[grp].extend(files)

    merged = dict(new_report)
    merged["machineId"] = machine_id
    merged["_machines"] = machines
    merged["stats"] = {
        "commands": all_commands,
        "commits": len(all_commits_set),
        "repos": len(all_repos),
        "filesModified": all_files,
    }
    merged["gitActivity"] = list(merged_git.values())
    merged["categories"] = dict(sorted(merged_categories.items(), key=lambda x: -x[1]))
    merged["activityByHour"] = dict(sorted(merged_hours.items()))
    # Deduplicate notable commands by command text
    seen_cmds = set()
    unique_notable = []
    for cmd in merged_notable:
        if cmd["command"] not in seen_cmds:
            seen_cmds.add(cmd["command"])
            unique_notable.append(cmd)
    merged["notableCommands"] = unique_notable[:30]
    merged["fileGroups"] = {k: v[:10] for k, v in sorted(merged_file_groups.items())}
    merged["summary"] = (
        f"{all_commands} terminal commands, {len(all_commits_set)} commits "
        f"across {len(all_repos)} repos, {all_files} files modified."
    )
    return merged


def main():
    import sys
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")

    report = generate_report(target_date)

    APP_PUBLIC.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if report:
        report["machineId"] = MACHINE_ID

        entry_file = APP_PUBLIC / f"{target_date}.json"
        if entry_file.exists():
            try:
                existing = json.loads(entry_file.read_text())
                report = merge_reports(existing, report, MACHINE_ID)
            except (json.JSONDecodeError, KeyError):
                pass

        snapshot = {k: v for k, v in report.items() if k != "_machines"}
        report["_machines"] = report.get("_machines", {})
        report["_machines"][MACHINE_ID] = snapshot

        entry_file.write_text(json.dumps(report, indent=2))
        print(f"Daily journal written: {target_date} ({report['stats']['commands']} cmds, {report['stats']['commits']} commits)")
    else:
        print(f"Daily journal written: {target_date} (empty day)")

    # Legacy markdown
    if report:
        md = generate_markdown(report)
        (OUTPUT_DIR / f"{target_date}.md").write_text(md)
    else:
        (OUTPUT_DIR / f"{target_date}.md").write_text(
            f"# Daily Journal — {datetime.strptime(target_date, '%Y-%m-%d').strftime('%A, %B %d, %Y')}\n\n> No activity recorded.\n"
        )


def generate_markdown(r: dict) -> str:
    lines = [f"# Daily Journal — {r['day']}, {r['display']}", "", f"> {r['summary']}", ""]
    if r["gitActivity"]:
        lines += ["## Git Activity", ""]
        for repo in r["gitActivity"]:
            lines.append(f"### {repo['repo']}")
            for c in repo["commits"]:
                lines.append(f"- `{c['hash']}` {c['time']} — {c['message']} ({c['author']})")
            lines.append("")
    if r["notableCommands"]:
        lines += ["## Notable Commands", ""]
        for cmd in r["notableCommands"]:
            lines.append(f"- `{cmd['time']}` `{cmd['command']}`")
        lines.append("")
    lines += ["---", f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*"]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
