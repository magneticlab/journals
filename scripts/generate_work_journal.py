#!/usr/bin/env python3
"""
Work Journal Generator — Claude Code Sessions
Produces digested, CEO-style structured reports.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

from config import get as get_config

_cfg = get_config()
HISTORY_FILE = Path.home() / _cfg["sources"]["claudeHistory"]
REPOS_DIR = Path.home() / _cfg["sources"]["reposDir"]
MACHINE_ID = _cfg.get("machineId", "default")
APP_PUBLIC = Path(__file__).parent.parent / "app" / "public" / "entries" / "work"
OUTPUT_DIR = Path(__file__).parent.parent / "work" / "entries"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_history_for_date(target_date):
    entries = []
    target_start = datetime.strptime(target_date, "%Y-%m-%d")
    start_ts = target_start.timestamp() * 1000
    end_ts = (target_start + timedelta(days=1)).timestamp() * 1000
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


def get_git_activity(target_date):
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
                cwd=str(repo_dir), capture_output=True, text=True, timeout=10)
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0][:7], "author": parts[1],
                        "message": parts[2],
                        "time": parts[3].split(" ")[1][:5] if " " in parts[3] else "",
                    })
            stat_result = subprocess.run(
                ["git", "log", f"--after={target_date} 00:00:00",
                 f"--before={target_date} 23:59:59", "--all",
                 "--stat", "--format=", "--no-merges"],
                cwd=str(repo_dir), capture_output=True, text=True, timeout=10)
            stat = ""
            for line in stat_result.stdout.strip().split("\n"):
                if "file" in line and "changed" in line:
                    stat = line.strip()
            if commits:
                activity.append({"repo": repo_name, "commits": commits, "stat": stat})
        except Exception:
            continue
    return activity


def get_project_label(path):
    if not path:
        return "unknown"
    parts = path.rstrip("/").split("/")
    return parts[-1] if parts else "unknown"


def extract_work_themes(entries):
    """Analyze session messages to extract work themes — no raw chats."""
    themes = defaultdict(list)
    for entry in entries:
        display = entry.get("display", "")
        if not display or display.startswith("/") or display.startswith("[Image") or len(display) < 10:
            continue
        text = display.lower()
        # Categorize by detected intent
        if any(w in text for w in ["design system", "token", "ds ", "component"]):
            themes["Design System"].append(display[:100])
        elif any(w in text for w in ["figma", "screenshot", "layout", "spacing", "padding"]):
            themes["Design & Layout"].append(display[:100])
        elif any(w in text for w in ["page", "section", "hero", "carousel", "card", "grid"]):
            themes["Page Building"].append(display[:100])
        elif any(w in text for w in ["animation", "lava", "ribbon", "blob", "background"]):
            themes["Animation & Effects"].append(display[:100])
        elif any(w in text for w in ["bug", "fix", "broken", "error", "not working", "issue"]):
            themes["Bug Fixes"].append(display[:100])
        elif any(w in text for w in ["commit", "push", "pull request", "pr ", "merge"]):
            themes["Git & Deployment"].append(display[:100])
        elif any(w in text for w in ["version", "v1", "v2", "v3", "v4", "v5", "variant"]):
            themes["Version Iteration"].append(display[:100])
        elif any(w in text for w in ["refactor", "restructur", "reorganiz", "clean"]):
            themes["Refactoring"].append(display[:100])
        elif any(w in text for w in ["email", "copy", "text", "content"]):
            themes["Content & Copy"].append(display[:100])
        elif any(w in text for w in ["roadmap", "plan", "strategy", "audit"]):
            themes["Planning & Strategy"].append(display[:100])
        else:
            themes["General Development"].append(display[:100])
    return dict(themes)


def derive_what_i_did(git_activity, themes, sessions_count):
    """Derive accomplishments — narrative summaries grouped by repo."""
    summaries = []

    for repo in git_activity:
        commits = [c for c in repo["commits"] if not c["message"].startswith("Merge")]
        if not commits:
            continue

        # Group commit messages into a narrative per repo
        msgs = [c["message"] for c in commits]
        if len(msgs) == 1:
            summaries.append(f"{repo['repo']}: {msgs[0]}")
        else:
            # Combine into a summary sentence
            summary = f"{repo['repo']}: {len(msgs)} commits — {msgs[0]}"
            if len(msgs) > 1:
                others = [m for m in msgs[1:3]]
                summary += ". Also: " + "; ".join(others)
                if len(msgs) > 3:
                    summary += f" (+{len(msgs) - 3} more)"
            summaries.append(summary)

    # Add theme summaries for high-activity areas
    for theme, messages in sorted(themes.items(), key=lambda x: -len(x[1])):
        if theme == "General Development":
            continue
        count = len(messages)
        if count >= 5:
            summaries.append(f"Focused on {theme.lower()} with {count} interactions across sessions")

    return summaries[:8]


def derive_activity_timeline(git_activity, themes):
    """Raw activity list — commits + theme interactions for expandable view."""
    items = []
    for repo in git_activity:
        for c in repo["commits"]:
            if c["message"].startswith("Merge"):
                continue
            items.append(f"{repo['repo']}: {c['message']}")

    for theme, messages in sorted(themes.items(), key=lambda x: -len(x[1])):
        if theme == "General Development":
            continue
        count = len(messages)
        if count >= 1:
            items.append(f"{theme}: {count} interaction(s)")

    return items[:20]


def derive_continued_and_roadblocks(entries, themes, sessions_count, total_commits, bug_count):
    """Derive 'Continued From Yesterday' and 'Roadblocks' from session patterns."""
    continued = []
    roadblocks = []

    # Continued: detect multi-day themes from session patterns
    top_themes = sorted(
        [(k, len(v)) for k, v in themes.items() if k != "General Development"],
        key=lambda x: -x[1]
    )
    for theme, count in top_themes[:2]:
        if count >= 5:
            continued.append(f"{theme} work ongoing — {count} interactions in this session, likely a multi-day effort")

    if total_commits == 0 and sessions_count > 0:
        continued.append("Exploration and research sessions without commits — work may span multiple days before shipping")

    # Roadblocks
    if bug_count >= 2:
        roadblocks.append(f"Hit {bug_count} bugs during the session — may indicate fragile areas that need architectural attention")

    if sessions_count >= 6:
        roadblocks.append(f"High context switching: {sessions_count} separate sessions may indicate difficulty maintaining focus or frequent interruptions")

    if total_commits > 0 and sessions_count > 0:
        ratio = total_commits / sessions_count
        if ratio < 0.5:
            roadblocks.append(f"Low commit-to-session ratio ({total_commits} commits across {sessions_count} sessions) — sessions may be exploratory or blocked")

    return continued, roadblocks


def derive_insights(git_activity, themes, sessions_count, total_commits,
                    total_insertions, total_deletions, total_files_changed, entries):
    """Generate strategic insights — observations about the day's work patterns."""
    insights = []

    # Volume insight
    if total_insertions > 1000:
        net = total_insertions - total_deletions
        insights.append(
            f"High-volume day: {total_insertions:,} lines added across {total_files_changed} files. "
            f"Net change of +{net:,} lines — {'significant new code' if net > 500 else 'mix of new code and refactoring'}."
        )
    elif total_insertions > 0 and total_deletions > total_insertions * 0.8:
        insights.append(
            f"Refactoring-heavy session: {total_deletions:,} deletions vs {total_insertions:,} insertions. "
            "Cleaning up technical debt or restructuring existing code."
        )

    # Multi-repo insight
    repos = [r["repo"] for r in git_activity]
    if len(repos) > 1:
        insights.append(
            f"Cross-project day spanning {len(repos)} repositories ({', '.join(repos)}). "
            "Context switching between projects may indicate parallel workstreams or dependencies."
        )

    # Theme diversity insight
    active_themes = [(k, len(v)) for k, v in themes.items() if k != "General Development" and len(v) >= 3]
    if len(active_themes) >= 3:
        top3 = [f"{t[0]} ({t[1]})" for t in sorted(active_themes, key=lambda x: -x[1])[:3]]
        insights.append(
            f"Diverse focus across {len(active_themes)} areas: {', '.join(top3)}. "
            "Breadth of work suggests design-to-implementation pipeline or sprint-style execution."
        )

    # Session depth insight
    if entries:
        session_map = {}
        for e in entries:
            sid = e.get("sessionId", "")
            session_map[sid] = session_map.get(sid, 0) + 1
        longest = max(session_map.values()) if session_map else 0
        if longest >= 30:
            insights.append(
                f"Deep work detected: longest session had {longest} messages — sustained focus on a complex task. "
                "This level of engagement typically produces the highest-quality output."
            )

    # Commit pattern insight
    if total_commits >= 5:
        feat_count = sum(1 for r in git_activity for c in r["commits"] if c["message"].startswith("feat"))
        fix_count = sum(1 for r in git_activity for c in r["commits"] if c["message"].startswith("fix"))
        if feat_count > fix_count:
            insights.append(
                f"Feature-forward day: {feat_count} feature commits vs {fix_count} fixes. "
                "Building momentum on new functionality rather than firefighting."
            )

    # Design system insight
    ds_count = len(themes.get("Design System", []))
    if ds_count >= 5:
        insights.append(
            "Significant design system investment today. Systematic token and component work "
            "compounds over time — every page built after this benefits from the foundation."
        )

    return insights[:6]


def derive_projects_wip(git_activity, entries):
    """Derive project tags from git and session data."""
    projects = set()
    for repo in git_activity:
        commit_count = len(repo["commits"])
        projects.add(f"{repo['repo']} — {commit_count} commit(s)")

    session_projects = set()
    for e in entries:
        proj = get_project_label(e.get("project", ""))
        if proj and proj not in [r["repo"] for r in git_activity]:
            session_projects.add(proj)
    for p in session_projects:
        projects.add(f"{p} — session work")

    return sorted(projects)


def compute_metrics(sessions, messages, commits, insertions, deletions,
                     files_changed, themes, entries, bug_count):
    """
    Evaluate the day's work across multiple dimensions.
    Each metric is 0-100 with a short rationale.

    Dimensions:
    - Output Volume: raw productivity — lines shipped, commits made
    - Complexity: variety of themes, files touched, multi-repo work
    - Focus: inverse of context switching — fewer sessions = more focus
    - Depth: messages per session — longer sessions = deeper engagement
    - Craft: ratio of feature/design work vs bug fixes
    - Momentum: commits relative to a strong baseline day (~10)
    """
    m = {}

    # Output Volume — based on insertions (log scale, 500+ is max)
    if insertions > 0:
        import math
        vol = min(int(math.log(insertions, 1.8) / math.log(3000, 1.8) * 100), 100)
    elif commits > 0:
        vol = min(commits * 15, 60)
    else:
        vol = 0
    m["volume"] = {"score": vol, "label": "Output Volume"}

    # Complexity — theme diversity + files + repos
    theme_count = len([t for t in themes if t != "General Development"])
    complexity = min(int((theme_count * 12 + files_changed * 2 + commits * 5) / 1.2), 100)
    m["complexity"] = {"score": complexity, "label": "Complexity"}

    # Focus — fewer sessions with more messages each = higher focus
    if sessions > 0:
        avg_msgs = messages / sessions
        # Sweet spot: 1-3 sessions with 20+ msgs each
        focus_raw = min(avg_msgs / 20 * 70 + max(0, (4 - sessions)) * 10, 100)
        focus = max(int(focus_raw), 10) if messages > 0 else 0
    else:
        focus = 0
    m["focus"] = {"score": focus, "label": "Focus"}

    # Depth — longest session length, message density
    if entries:
        session_lengths = {}
        for e in entries:
            sid = e.get("sessionId", "")
            if sid not in session_lengths:
                session_lengths[sid] = 0
            session_lengths[sid] += 1
        longest = max(session_lengths.values()) if session_lengths else 0
        depth = min(int(longest / 30 * 80 + theme_count * 3), 100)
    else:
        depth = 0
    m["depth"] = {"score": depth, "label": "Depth"}

    # Craft — feature + design work vs bugs and fixes
    craft_themes = sum(len(themes.get(t, [])) for t in
                       ["Design System", "Design & Layout", "Page Building",
                        "Animation & Effects", "Planning & Strategy"])
    total_themed = sum(len(v) for v in themes.values()) or 1
    craft = min(int((craft_themes / total_themed) * 100 + (0 if bug_count > 2 else 15)), 100)
    m["craft"] = {"score": craft, "label": "Craft"}

    # Momentum — commits vs a baseline of 8-10/day
    momentum = min(int(commits / 8 * 100), 100) if commits > 0 else 0
    m["momentum"] = {"score": momentum, "label": "Momentum"}

    return m


def generate_report(target_date):
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    day_name = WEEKDAYS[dt.weekday()]
    entries = load_history_for_date(target_date)
    git_activity = get_git_activity(target_date)

    # Group sessions
    sessions_map = defaultdict(list)
    for entry in entries:
        sessions_map[entry.get("sessionId", "unknown")].append(entry)

    if not entries and not git_activity:
        return None

    sessions_count = len(sessions_map)
    total_messages = len(entries)
    total_commits = sum(len(r["commits"]) for r in git_activity)

    # Parse volume metrics from git stat strings
    total_insertions = 0
    total_deletions = 0
    total_files_changed = 0
    import re
    for repo in git_activity:
        stat = repo.get("stat", "")
        if stat:
            fm = re.search(r'(\d+) file', stat)
            im = re.search(r'(\d+) insertion', stat)
            dm = re.search(r'(\d+) deletion', stat)
            if fm: total_files_changed += int(fm.group(1))
            if im: total_insertions += int(im.group(1))
            if dm: total_deletions += int(dm.group(1))

    # Time range
    time_range = ""
    if entries:
        first_ts = entries[0]["timestamp"] / 1000
        last_ts = entries[-1]["timestamp"] / 1000
        time_range = f"{datetime.fromtimestamp(first_ts).strftime('%H:%M')}–{datetime.fromtimestamp(last_ts).strftime('%H:%M')}"

    # Derive structured content
    themes = extract_work_themes(entries)
    what_i_did = derive_what_i_did(git_activity, themes, sessions_count)
    activity_timeline = derive_activity_timeline(git_activity, themes)
    projects_wip = derive_projects_wip(git_activity, entries)

    # Docs created — from commit messages containing "doc", "plan", "audit", "report"
    docs_created = []
    for repo in git_activity:
        for c in repo["commits"]:
            msg_lower = c["message"].lower()
            if any(w in msg_lower for w in ["doc", "plan", "audit", "report", "research", "brief"]):
                docs_created.append({
                    "title": c["message"],
                    "description": f"{repo['repo']} · {c['hash']}",
                })

    # Determine what went right / could be better
    went_right = ""
    could_be_better = ""

    if total_commits > 0 and sessions_count > 0:
        went_right = f"Productive day with {total_commits} commit(s) across {len(git_activity)} repo(s) during {sessions_count} Claude session(s) spanning {time_range}."
    elif total_commits > 0:
        went_right = f"{total_commits} commit(s) shipped across {len(git_activity)} repo(s)."
    elif sessions_count > 0:
        went_right = f"{sessions_count} exploration session(s) with {total_messages} messages — active R&D day."

    # Detect potential friction from themes
    bug_count = len(themes.get("Bug Fixes", []))
    if bug_count >= 2:
        could_be_better = f"Hit {bug_count} bugs during the session — check if recurring patterns need architectural fixes."
    elif sessions_count > 5:
        could_be_better = f"High session count ({sessions_count}) may indicate context switching — consider consolidating related work."
    elif total_commits == 0 and sessions_count > 0:
        could_be_better = "Sessions ran but no commits — work may be exploratory or incomplete."

    # Insights
    insights = derive_insights(
        git_activity, themes, sessions_count, total_commits,
        total_insertions, total_deletions, total_files_changed, entries
    )

    # Continued from yesterday + roadblocks
    continued, roadblocks = derive_continued_and_roadblocks(
        entries, themes, sessions_count, total_commits, bug_count
    )

    # Evaluation metrics — scored 0-100
    metrics = compute_metrics(
        sessions_count, total_messages, total_commits, total_insertions,
        total_deletions, total_files_changed, themes, entries, bug_count
    )

    return {
        "date": target_date,
        "day": day_name,
        "display": dt.strftime("%B %d, %Y"),
        "generatedAt": datetime.now().isoformat(),
        "metrics": metrics,
        "stats": {
            "sessions": sessions_count,
            "messages": total_messages,
            "commits": total_commits,
            "repos": len(git_activity),
            "timeRange": time_range,
            "linesAdded": total_insertions,
            "linesRemoved": total_deletions,
            "filesChanged": total_files_changed,
        },
        "wentRight": went_right,
        "couldBeBetter": could_be_better,
        "whatIDid": what_i_did,
        "activityTimeline": activity_timeline,
        "insights": insights,
        "continuedFromYesterday": continued,
        "roadblocks": roadblocks,
        "themes": {k: len(v) for k, v in sorted(themes.items(), key=lambda x: -len(x[1]))},
        "projectsWip": projects_wip,
        "docsCreated": docs_created,
        "gitActivity": git_activity,
        "summary": f"{sessions_count} session(s), {total_messages} msgs, {total_commits} commit(s) across {len(git_activity)} repo(s)",
    }


def merge_reports(existing, new_report, machine_id):
    """Merge this machine's report with existing data from other machines."""
    machines = existing.get("_machines", {})

    # If existing report was from a different machine with no _machines yet, adopt it
    if not machines and existing.get("machineId") and existing["machineId"] != machine_id:
        machines[existing["machineId"]] = existing

    # Store this machine's contribution (without _machines to avoid circular refs)
    machines[machine_id] = {k: v for k, v in new_report.items() if k != "_machines"}

    if len(machines) <= 1:
        new_report["_machines"] = machines
        new_report["machineId"] = machine_id
        return new_report

    # Aggregate stats across all machines
    all_sessions = 0
    all_messages = 0
    all_commits_set = set()
    all_repos = set()
    all_lines_added = 0
    all_lines_removed = 0
    all_files_changed = 0
    time_starts = []
    time_ends = []
    merged_git = {}
    merged_themes = defaultdict(int)
    merged_what = []
    merged_timeline = []
    merged_insights = []
    merged_projects = []

    for mid, rpt in machines.items():
        stats = rpt.get("stats", {})
        all_sessions += stats.get("sessions", 0)
        all_messages += stats.get("messages", 0)
        all_lines_added += stats.get("linesAdded", 0)
        all_lines_removed += stats.get("linesRemoved", 0)
        all_files_changed += stats.get("filesChanged", 0)

        tr = stats.get("timeRange", "")
        if "–" in tr:
            s, e = tr.split("–")
            time_starts.append(s)
            time_ends.append(e)

        # Merge git activity — deduplicate commits by hash
        for repo in rpt.get("gitActivity", []):
            rname = repo["repo"]
            if rname not in merged_git:
                merged_git[rname] = {"repo": rname, "commits": [], "stat": repo.get("stat", "")}
            seen_hashes = {c["hash"] for c in merged_git[rname]["commits"]}
            for c in repo["commits"]:
                if c["hash"] not in seen_hashes:
                    merged_git[rname]["commits"].append(c)
                    all_commits_set.add(c["hash"])
            all_repos.add(rname)

        for theme, count in rpt.get("themes", {}).items():
            merged_themes[theme] = max(merged_themes[theme], count)

        merged_what.extend(rpt.get("whatIDid", []))
        merged_timeline.extend(rpt.get("activityTimeline", []))
        merged_insights.extend(rpt.get("insights", []))
        merged_projects.extend(rpt.get("projectsWip", []))

    time_range = ""
    if time_starts and time_ends:
        time_range = f"{min(time_starts)}–{max(time_ends)}"

    # Build merged report using new_report as base for date/day/display
    merged = dict(new_report)
    merged["machineId"] = machine_id
    merged["_machines"] = machines
    merged["stats"] = {
        "sessions": all_sessions,
        "messages": all_messages,
        "commits": len(all_commits_set),
        "repos": len(all_repos),
        "timeRange": time_range,
        "linesAdded": all_lines_added,
        "linesRemoved": all_lines_removed,
        "filesChanged": all_files_changed,
    }
    merged["gitActivity"] = list(merged_git.values())
    merged["themes"] = dict(sorted(merged_themes.items(), key=lambda x: -x[1]))
    merged["whatIDid"] = list(dict.fromkeys(merged_what))[:8]
    merged["activityTimeline"] = list(dict.fromkeys(merged_timeline))[:20]
    merged["insights"] = list(dict.fromkeys(merged_insights))[:6]
    merged["projectsWip"] = sorted(set(merged_projects))
    merged["summary"] = (
        f"{all_sessions} session(s), {all_messages} msgs, "
        f"{len(all_commits_set)} commit(s) across {len(all_repos)} repo(s)"
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

        # Merge with existing data from other machines
        entry_file = APP_PUBLIC / f"{target_date}.json"
        if entry_file.exists():
            try:
                existing = json.loads(entry_file.read_text())
                report = merge_reports(existing, report, MACHINE_ID)
            except (json.JSONDecodeError, KeyError):
                pass

        # Store a snapshot for multi-machine merge (avoid circular refs)
        snapshot = {k: v for k, v in report.items() if k != "_machines"}
        report["_machines"] = report.get("_machines", {})
        report["_machines"][MACHINE_ID] = snapshot

        entry_file.write_text(json.dumps(report, indent=2))
        print(f"Work: {target_date} ({report['stats']['sessions']}s, {report['stats']['commits']}c)")
    else:
        print(f"Work: {target_date} (empty)")


if __name__ == "__main__":
    main()
