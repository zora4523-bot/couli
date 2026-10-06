#!/usr/bin/env python3
"""Local planning & task board: parse the planning docs and the engineering ledger live.

Requires Python >= 3.9, with no third-party dependencies.
Run from any directory:
  python3 /path/to/couli/scripts/kanban.py            serve http://127.0.0.1:8766/
  python3 /path/to/couli/scripts/kanban.py --check    parse once, report tables that went unread
  python3 /path/to/couli/scripts/kanban.py --json     print the board data
  python3 /path/to/couli/scripts/kanban.py --export ~/Desktop/couli-board.html   single-file snapshot

Both repositories are read through git at their remote main, so the board follows what
has been merged even when the local checkouts lag behind. Unless --fetch 0 is given, each
remote main is fetched into the private ref refs/kanban/main; no branch, remote-tracking
ref or working file is touched. --local reads the planning files next to this script
instead, to preview edits that are not merged yet. The page reloads its data whenever a
source changes.
"""

import argparse
import csv
from datetime import date, datetime, timedelta, timezone
from fnmatch import fnmatchcase
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "kanban"
PLAN = ROOT / "规划"
RULES = PLAN / "08_业务规则"
CAPS = PLAN / "09_平台能力验证"
TZ = timezone(timedelta(hours=8))
YEAR = 2026
W0_START = date(2026, 9, 29)
FETCH_REF = "refs/kanban/main"
REF_LABEL = {
    FETCH_REF: "远端 main（看板自己拉取）", "refs/remotes/origin/main": "origin/main（本机上次 fetch 到的）",
    "HEAD": "本地检出（没有远端 main 的引用，可能落后或含未合并的内容）",
}
LINES = ("CT", "B1", "B2", "B3", "F1", "APP", "HM", "QA")
TASK_ID = re.compile(r"(?<![A-Za-z0-9-])((?:CT|B1|B2|B3|F1|APP|HM|QA)-\d{2})(?![0-9])")
LEDGER_ID = re.compile(r"((?:CT|B1|B2|B3|F1|APP|HM|QA)-\d{2})([a-z]*)\Z")
STATUSES = ("done", "in_progress", "open", "blocked", "deferred", "void")
STATUS_LABEL = {"done": "已完成", "in_progress": "进行中", "open": "待办", "blocked": "被阻塞", "deferred": "远期", "void": "作废"}


# ---------------------------------------------------------------- markdown

class Docs:
    """The planning text: the files next to this script, or one commit of the repository."""

    def __init__(self):
        self.commit = None
        self.files = {}

    def use(self, repo, sha):
        """Read from the given commit from now on; sha None goes back to the working tree."""
        if sha and sha != self.commit:
            self.files = repo.files(sha, rel(PLAN), rel(DOC_DESIGN))
        self.commit = sha

    def text(self, path):
        return self.files[rel(path)] if self.commit else path.read_text(encoding="utf-8")

    def stamp(self, path):
        return self.commit or path.stat().st_mtime_ns

    def glob(self, directory, pattern):
        if not self.commit:
            return sorted(directory.glob(pattern))
        prefix = rel(directory) + "/"
        names = (name[len(prefix):] for name in self.files if name.startswith(prefix))
        return sorted(directory / name for name in names if "/" not in name and fnmatchcase(name, pattern))


DOCS = Docs()


def split_row(line):
    """Split one GFM table row on unescaped pipes."""
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", text)]


def is_separator(cells):
    return all(cell and set(cell) <= set("-: ") for cell in cells)


class Table:
    def __init__(self, path, headings, header, line):
        self.path = path
        self.headings = headings      # heading texts from the document title down
        self.header = header
        self.line = line
        self.rows = []                # (line number, cells)
        self.short = []               # line numbers of rows that had fewer cells than the header

    @property
    def section(self):
        return self.headings[-1] if self.headings else ""

    def column(self, *names):
        """Index of the first header cell containing any of the given fragments."""
        for index, cell in enumerate(self.header):
            if any(name in cell for name in names):
                return index
        return None


TABLE_CACHE = {}


def tables(path):
    """Every table in a Markdown file, each with its heading path; a missing file has none."""
    try:
        stamp = DOCS.stamp(path)
        if TABLE_CACHE.get(path, (None,))[0] != stamp:
            TABLE_CACHE[path] = (stamp, scan_tables(path, DOCS.text(path)))
    except (OSError, KeyError):
        return []
    return TABLE_CACHE[path][1]


def scan_tables(path, text):
    found = []
    stack = []
    current = None
    fenced = False
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            current = None
            continue
        if fenced:
            continue
        heading = re.match(r"(#{1,6})\s+(.*)", line)
        if heading:
            level = len(heading.group(1))
            stack = [item for item in stack if item[0] < level] + [(level, heading.group(2).strip())]
            current = None
            continue
        if not stripped.startswith("|"):
            current = None
            continue
        cells = split_row(line)
        if current is None:
            current = Table(path, [text for _, text in stack], cells, number)
            found.append(current)
        elif not is_separator(cells):
            if len(cells) < len(current.header):
                current.short.append(number)
                cells += [""] * (len(current.header) - len(cells))
            current.rows.append((number, cells))
    return found


def short_rows():
    """Rows with missing cells in the tables read so far; they were padded with blanks."""
    for path, (_, found) in sorted(TABLE_CACHE.items()):
        lines = [number for table in found for number in table.short]
        if lines:
            yield f"{rel(path)} 第 {'、'.join(map(str, lines[:6]))} 行的格数比表头少，缺的格按空白处理"


def plain(text):
    """Strip the inline Markdown that gets in the way of matching and short titles."""
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\*\*|`", "", text).strip()


def clip(text, limit):
    text = plain(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip("，、；：( （") + "…"


def rel(path):
    return path.relative_to(ROOT).as_posix()


def source(path, line):
    return {"file": rel(path), "line": line}


# ---------------------------------------------------------------- git & ledger

# Set by git while it runs a hook; inherited, they would redirect every call to that repository.
GIT_LOCATION = frozenset({
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_PREFIX",
})


def git(repo, *args, data=None, timeout=30):
    """Run git read-only; return stdout bytes, or None when the command fails."""
    env = {name: value for name, value in os.environ.items() if name not in GIT_LOCATION}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        done = subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


def git_text(repo, *args, **kwargs):
    out = git(repo, *args, **kwargs)
    return None if out is None else out.decode("utf-8", "replace").strip()


def sibling(name):
    """A sibling of the main checkout; also correct when this script runs in a worktree."""
    common = git_text(ROOT, "rev-parse", "--path-format=absolute", "--git-common-dir")
    main = Path(common).parent if common else ROOT
    for base in (main.parent, ROOT.parent):
        if (base / name).is_dir():
            return base / name
    return main.parent / name


def yaml_scalar(text):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    comment = re.search(r"\s+#", text)
    if comment:
        text = text[: comment.start()].rstrip()
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return {"null": None, "~": None, "": None, "true": True, "false": False}.get(text, text)


def yaml_inline_list(text):
    inner = text.strip()[1:-1].strip()
    if not inner:
        return []
    return [yaml_scalar(item) for item in re.findall(r"""'[^']*'|"[^"]*"|[^,]+""", inner)]


def ledger_yaml(text):
    """Read the flat subset of YAML the task ledger uses: scalars, inline and block lists."""
    data = {}
    key = None
    for line in text.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.match(r"([A-Za-z_][\w-]*):(?:\s+(.*)|\s*)\Z", line)
        if top:
            key, value = top.group(1), (top.group(2) or "").strip()
            if not value:
                data[key] = None
            elif value.startswith("[") and value.endswith("]"):
                data[key] = yaml_inline_list(value)
            elif value.startswith("{"):
                data[key] = {}
            else:
                data[key] = yaml_scalar(value)
            continue
        item = re.match(r"\s+-\s+(.*)\Z", line)
        if item and key is not None:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(yaml_scalar(item.group(1)))
    return data


def cat_blobs(repo, ref, paths):
    """Read many files of one commit with a single git process."""
    request = "".join(f"{ref}:{path}\n" for path in paths).encode("utf-8")
    out = git(repo, "cat-file", "--batch", data=request)
    blobs = {}
    if out is None:
        return blobs
    offset = 0
    for path in paths:
        end = out.find(b"\n", offset)
        if end < 0:
            break
        header = out[offset:end].split()
        offset = end + 1
        if len(header) != 3 or header[1] != b"blob":
            continue
        size = int(header[2])
        blobs[path] = out[offset : offset + size].decode("utf-8", "replace")
        offset += size + 1
    return blobs


class Repo:
    """A git repository, read at the freshest main this machine knows of."""

    def __init__(self, path):
        self.path = Path(path)
        self.fetch_at = None
        self.fetch_error = None

    @property
    def available(self):
        return (self.path / ".git").exists()

    def ref(self):
        """(name, sha, commit time) of main: the newer of the private fetch ref and origin/main.

        The checkout is only the last resort, for a repository without a remote; a checked-out
        branch can carry work that is not merged.
        """
        best = None
        for name in (FETCH_REF, "refs/remotes/origin/main", "HEAD"):
            if name == "HEAD" and best:
                break
            line = git_text(self.path, "log", "-1", "--format=%H %ct", name, "--")
            if not line:
                continue
            sha, stamp = line.split()
            if best is None or int(stamp) > best[2]:
                best = (name, sha, int(stamp))
        return best

    def files(self, ref, *roots):
        """Text of every file under the given paths at one commit."""
        listing = git(self.path, "ls-tree", "-r", "-z", "--name-only", ref, "--", *roots) or b""
        return cat_blobs(self.path, ref, [name for name in listing.decode("utf-8", "replace").split("\0") if name])

    def fetch(self):
        """Refresh the private ref only.

        --refmap= switches off the configured refspec, which would otherwise move origin/main
        as a side effect; FETCH_HEAD is not written either, so other sessions see no change.
        """
        out = git(
            self.path, "-c", "gc.auto=0", "-c", "maintenance.auto=false", "fetch", "--quiet", "--no-tags",
            "--no-write-fetch-head", "--refmap=", "origin", f"+refs/heads/main:{FETCH_REF}", timeout=90,
        )
        if out is not None:
            self.fetch_at, self.fetch_error = datetime.now(TZ), None
        else:
            since = f"，用的是 {self.fetch_at:%H:%M} 拉到的提交" if self.fetch_at else "，用的是本机已有的提交"
            self.fetch_error = "远端 main 拉取失败（网络或凭据）" + since
        return out is not None

    def web_url(self):
        url = git_text(self.path, "remote", "get-url", "origin") or ""
        match = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
        return f"https://github.com/{match.group(1)}" if match else None

    def ledger(self, ref):
        entries = []
        for path, text in sorted(self.files(ref, "ops/tasks").items()):
            if not path.endswith((".yaml", ".yml")):
                continue
            data = ledger_yaml(text)
            ident = str(data.get("id") or Path(path).stem)
            entries.append({
                "id": ident,
                "title": str(data.get("title") or ""),
                "type": data.get("type"),
                "status": str(data.get("status") or "todo"),
                "pr": data.get("pr") if isinstance(data.get("pr"), int) else None,
                "deps": [str(dep) for dep in data.get("deps") or []],
                "impl": data.get("impl"),
                "tester": data.get("tester"),
                "archived": "/archive/" in path,
                "path": path,
            })
        return entries


# ---------------------------------------------------------------- 05：任务、阶段、周

DOC_TASKS = PLAN / "05_里程碑与任务拆分.md"
DOC_OVERVIEW = PLAN / "00_总览与决策.md"
WEEK = re.compile(r"W(\d+)(?:\s*[–—-]\s*W(\d+))?")
LINE_NAMES = {
    "CT": "接口与公共规格", "B1": "交易后端", "B2": "资金后端", "B3": "Agent 后端",
    "F1": "H5 + 后台", "APP": "iOS / Android", "HM": "鸿蒙", "QA": "质量",
}


def strip_parens(text):
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"（[^（）]*）|\([^()]*\)", "", text)
    return text


def week_numbers(text):
    """Weeks named outside parentheses, ranges expanded: 'W2–W3（影子）；W4–W5' -> 2..5."""
    weeks = set()
    for first, last in WEEK.findall(strip_parens(text)):
        weeks.update(range(int(first), int(last or first) + 1))
    return sorted(weeks)


def first_clause(text):
    """Text up to the first sentence break that is not inside brackets."""
    depth = 0
    for index, char in enumerate(text):
        if char in "（(":
            depth += 1
        elif char in "）)":
            depth = max(depth - 1, 0)
        elif char in "；。" and depth == 0:
            return text[:index]
    return text


def expand_task_ids(text):
    """Task ids in running text, with 'B1-02…10' style ranges expanded."""
    ids = []
    for line, first, last in re.findall(r"((?:CT|B1|B2|B3|F1|APP|HM|QA))-(\d{2})(?:\s*[…~～]\s*(?:\1-)?(\d{2}))?(?!\d)", text):
        for number in range(int(first), int(last or first) + 1):
            ids.append(f"{line}-{number:02d}")
    return list(dict.fromkeys(ids))


def parse_weeks(warn):
    year = YEAR
    weeks = []
    for table in tables(DOC_TASKS):
        if table.header[:2] != ["周", "日期"]:
            continue
        for line, cells in table.rows:
            span = re.match(r"(\d{2})-(\d{2})\s*→\s*(\d{2})-(\d{2})", cells[1])
            number = re.fullmatch(r"W(\d+)", cells[0])
            if not span or not number:
                continue
            m1, d1, m2, d2 = map(int, span.groups())
            try:
                start, end = date(year, m1, d1), date(year, m2, d2)
            except ValueError:
                warn(f"05 周计划 {cells[0]}（第 {line} 行）的日期不存在：{cells[1]}")
                continue
            weeks.append({
                "id": cells[0], "number": int(number.group(1)), "range": cells[1].replace(" ", ""),
                "start": start.isoformat(), "end": end.isoformat(), "src": source(DOC_TASKS, line),
            })
    if not weeks:
        warn("05 §1 周计划表没有读到（表头应为「周 | 日期 | …」）；周次筛选与「已过计划周」不可用")
    return weeks


def parse_stages(warn):
    stages = []
    for table in tables(DOC_TASKS):
        if table.header[:2] != ["阶段", "交付的用户结果"]:
            continue
        for line, cells in table.rows:
            label = plain(cells[0])
            ident = re.match(r"S\d", label)
            if not ident:
                continue
            members = re.sub(r"取代\s*(?:CT|B1|B2|B3|F1|APP|HM|QA)-\d{2}|排在[^（）()]*之后", "", cells[2])
            stages.append({
                "id": ident.group(0), "name": label[len(ident.group(0)):].strip(), "result": cells[1],
                "tasks_raw": cells[2], "exit": cells[3], "weeks": plain(cells[4]),
                "task_ids": expand_task_ids(members), "src": source(DOC_TASKS, line),
            })
    if not stages:
        warn("05 §0 阶段表没有读到（表头应为「阶段 | 交付的用户结果 | …」）；任务不标阶段")
    return stages


def parse_tasks(warn):
    tasks = []
    for table in tables(DOC_TASKS):
        if not table.header or table.header[0] != "任务":
            continue
        when_at = table.column("周", "截止")
        deps_at = table.column("依赖")
        refs_at = table.column("关联")
        extra_at = table.column("验收", "产出")
        share_at = exact(table, "线")
        for line, cells in table.rows:
            ident = re.fullmatch(r"(CT|B1|B2|B3|F1|APP|HM|QA)-\d{2}", plain(cells[0]))
            if not ident:
                continue
            if len(cells) > len(table.header):
                warn(f"05 任务 {ident.group(0)}（第 {line} 行）的格数比表头多，可能有未转义的竖线")
            if deps_at is None and ident.group(1) not in ("HM", "QA") and not any(task["line"] == ident.group(1) for task in tasks):
                warn(f"05 {ident.group(1)} 线的任务表没有「依赖」列，任务之间的依赖读不到")
            cell = lambda at: cells[at] if at is not None and at < len(cells) else ""
            content, when = cells[1], plain(cell(when_at))
            weeks = week_numbers(when)
            void = when.startswith("作废") or plain(content).startswith("已作废")
            deferred = bool(re.match(r"P[12]\b|后续接入", when)) or "未排期" in when
            deps_raw = cell(deps_at)
            deps_plain = strip_parens(plain(deps_raw))
            refs = cell(refs_at)
            tasks.append({
                "id": ident.group(0), "line": ident.group(1), "order": len(tasks),
                "title": clip(first_clause(plain(content)), 72), "content": content,
                "when": when, "when_short": clip(strip_parens(when) or when, 18),
                "weeks": [f"W{number}" for number in weeks],
                "week_rank": weeks[0] if weeks else 99, "week_last": weeks[-1] if weeks else None,
                "deps": [dep for dep in expand_task_ids(deps_plain) if dep != ident.group(0)],
                "deps_raw": "" if plain(deps_raw) in ("—", "-", "") else deps_raw,
                "human_deps": [part.strip() for part in re.findall(r"人：[^；;]*", deps_plain)],
                "share": plain(cell(share_at)),
                "refs": refs if refs_at != extra_at else "",
                "extra": "" if plain(cell(extra_at)) in ("—", "-", "") else cell(extra_at),
                "extra_label": table.header[extra_at] if extra_at is not None else "",
                "plan_state": "void" if void else "deferred" if deferred else "active",
                "stages": [], "src": source(DOC_TASKS, line),
            })
    counts = {line: sum(task["line"] == line for task in tasks) for line in LINES}
    missing = [line for line, count in counts.items() if not count]
    if missing:
        warn(f"05 §3 没有读到这些线的任务表：{'、'.join(missing)}（表头首列应为「任务」）")
    return tasks


def parse_milestones(weeks, today, warn):
    stones = []
    by_week = {week["number"]: week for week in weeks}
    for table in tables(DOC_OVERVIEW):
        if table.header[:2] != ["里程碑", "时间"]:
            continue
        for line, cells in table.rows:
            label = plain(cells[0])
            ident = re.match(r"M\d|P1", label)
            if not ident:
                continue
            when = plain(cells[1])
            day = None
            explicit = re.search(r"(?<![\d-])(?:(\d{4})-)?(\d{1,2})-(\d{2})(?![\d-])", when)
            week = re.search(r"W(\d+)", when)
            if explicit:
                try:
                    day = date(int(explicit.group(1) or YEAR), int(explicit.group(2)), int(explicit.group(3)))
                except ValueError:
                    warn(f"00 里程碑 {ident.group(0)}（第 {line} 行）的日期不存在：{when}")
            if day:
                pass
            elif week and int(week.group(1)) in by_week:
                edge = "start" if "起" in when else "end"
                day = date.fromisoformat(by_week[int(week.group(1))][edge])
            stones.append({
                "id": ident.group(0), "name": label[len(ident.group(0)):].strip(), "when": when,
                "date": day.isoformat() if day else None, "stage": cells[2], "exit": cells[3],
                "when_state": "past" if day and day < today else "future", "src": source(DOC_OVERVIEW, line),
            })
    upcoming = [stone for stone in stones if stone["date"] and stone["when_state"] == "future"]
    if upcoming:
        min(upcoming, key=lambda stone: stone["date"])["when_state"] = "next"
    if not stones:
        warn("00 §5 里程碑表没有读到（表头应为「里程碑 | 时间 | …」）")
    return stones


# ---------------------------------------------------------------- 任务 × 台账

LEDGER_STATE_LABEL = {"done": "已合并", "in_progress": "在途", "todo": "待开工"}


def join_ledger(tasks, entries, inflight, merged, warn):
    """Attach ledger entries to the 05 task they were split from and derive each task's state."""
    by_parent = {}
    orphans = []
    for entry in entries:
        match = LEDGER_ID.match(entry["id"])
        parent = match.group(1) if match else None
        running = inflight.get(entry["id"])
        stale = entry["status"] != "done" and entry["id"] in merged
        state = "done" if entry["status"] == "done" or stale else "in_progress" if running else "todo"
        item = {**entry, "state": state, "step": (running or {}).get("step") if state == "in_progress" else None,
                "state_label": "已合并（台账还没改成 done）" if stale else LEDGER_STATE_LABEL[state]}
        if stale:
            item["pr"] = merged[entry["id"]]
        if parent and any(task["id"] == parent for task in tasks):
            by_parent.setdefault(parent, []).append(item)
        else:
            orphans.append(item)
    for task in tasks:
        subs = sorted(by_parent.get(task["id"], []), key=lambda item: item["id"])
        task["ledger"] = subs
        if task["plan_state"] != "active":
            task["state"] = task["plan_state"]
        elif not subs:
            task["state"] = "planned"
        elif all(item["state"] == "done" for item in subs):
            # The ledger does not say whether a task is fully split. Tables created ahead of the
            # module they belong to are the one case it does show: the work itself has not begun.
            ahead = all(item["type"] == "migration" for item in subs)
            task["state"] = "in_progress" if ahead else "merged"
            if ahead:
                task["note"] = "台账里只合并了建表迁移，功能本身还没有拆出任务"
        elif all(item["state"] == "todo" for item in subs):
            task["state"] = "todo"
        else:
            task["state"] = "in_progress"
    if orphans:
        warn("台账里有 " + str(len(orphans)) + " 个任务对不上 05 的编号：" + "、".join(item["id"] for item in orphans[:8]))
    return orphans


def tally(items, key):
    counts = {}
    for item in items:
        counts[item[key]] = counts.get(item[key], 0) + 1
    return counts



# ---------------------------------------------------------------- 在途状态与代码仓库指标

STEP_LABEL = {
    "ready": "排队", "spec": "写规则测试", "doing": "实现中", "verify": "容器验证", "review": "评审中",
    "longrun": "长跑测试", "pr": "已开 PR 待合并", "blocked": "卡住", "ask": "等负责人", "stale": "规划变更待同步",
}


LEASE = timedelta(minutes=20)       # tools/ops/lock.ts in the code repository


def read_json(path):
    """A JSON object from a file; anything else, or an unreadable file, reads as empty."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def expired(stamp, now, grace=timedelta(0)):
    """Whether an ISO timestamp plus a grace period lies in the past; unreadable ones do not count."""
    try:
        moment = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return moment + grace < now
    except (ValueError, TypeError, OverflowError):
        return False


def inflight_files(runs):
    if not runs.is_dir():
        return []
    return [runs / "state", runs / "claims", *sorted((runs / "state").glob("*.json")),
            *sorted((runs / "claims").glob("*/holder.json"))]


def read_inflight(runs):
    """Tasks some session is working on: a claim exists, or the state file left 'ready'.

    State files are not cleaned up after a merge, so the caller applies this only to
    ledger entries that are still todo.
    """
    running = {}
    now = datetime.now(timezone.utc)
    if not runs.is_dir():
        return running
    for path in (runs / "state").glob("*.json"):
        data = read_json(path)
        state = str(data.get("state") or "ready")
        if state != "ready":
            running[path.stem] = {"step": STEP_LABEL.get(state, state), "session": data.get("owner_session"),
                                  "expired": expired(data.get("lease_until"), now)}
    claims = runs / "claims"
    for claim in sorted(claims.iterdir()) if claims.is_dir() else []:
        if not claim.is_dir() or claim.name.endswith(".takeover"):
            continue
        holder = read_json(claim / "holder.json")
        entry = running.setdefault(claim.name, {"step": "已认领", "session": None, "expired": False})
        entry["session"] = holder.get("session") or entry["session"]
        entry["expired"] = entry["expired"] or expired(holder.get("heartbeat_at"), now, LEASE)
    for entry in running.values():
        if entry["expired"]:
            entry["step"] += "（认领已过期，其他会话可接手）"
    return running


def merged_titles(code, ref):
    """Task ids named at the start of a commit title on main: merged, whatever the ledger says."""
    log = git_text(code.path, "log", "--format=%s", ref, "--") or ""
    merged = {}
    for title in log.split("\n"):
        match = re.match(r"((?:CT|B1|B2|B3|F1|APP|HM|QA)-\d{2}[a-z]*)[：:\s]", title)
        if match:
            number = re.search(r"\(#(\d+)\)\s*\Z", title)
            merged.setdefault(match.group(1), int(number.group(1)) if number else None)
    return merged


def code_metrics(code, ref, planning):
    """Facts about the code repository that say how far development is, not planning."""
    metrics = {}
    text = git_text(code.path, "show", f"{ref}:contracts/openapi.yaml")
    if text:
        total = planned = 0
        inside = False
        for line in text.split("\n"):
            if re.match(r"\S", line):
                inside = line.startswith("paths:")
            elif inside and re.match(r"    (get|put|post|delete|patch):\s*\Z", line):
                total += 1
            elif inside and re.match(r"      x-implementation:\s*planned\b", line):
                planned += 1
        metrics["operations"] = {"total": total, "planned": planned}
    records = git_text(code.path, "show", f"{ref}:evidence/acceptance/records.csv")
    rows = list(csv.reader(io.StringIO(records))) if records else []
    result_at = rows[0].index("结果") if rows and "结果" in rows[0] else None
    metrics["acceptance"] = {
        "exists": records is not None,
        "rows": max(len(rows) - 1, 0),
        "passed": sum(1 for row in rows[1:] if result_at is not None and len(row) > result_at
                      and row[result_at].strip() in ("pass", "waived")),
    }
    spec_ref = git_text(code.path, "show", f"{ref}:SPEC_REF")
    if spec_ref and re.fullmatch(r"[0-9a-f]{40}", spec_ref):
        behind = git_text(ROOT, "rev-list", "--count", f"{spec_ref}..{planning}")
        metrics["spec_ref"] = {"sha": spec_ref[:7], "behind": int(behind) if behind and behind.isdigit() else None}
    return metrics


# ---------------------------------------------------------------- 状态归类

DONE_WORD = (r"已定|已确认|已完成|已交付|已处理|已结案|已落实|已改|已补|已覆盖|已按默认处理|当前基线|负责人选定|负责人自行处理"
             r"|已开通|已获批|已备案|已到位|已提供|已答复|已同意|已签约|已取得|已收到|已拿到")
VOID_WORD = r"已取消|取消|不再适用|不再处理|风险登记|转入|作废|废弃|不采纳|无需|不需要"
OPEN_WORD = r"待(?!遇)|未处理|未回答|未定|未开始|未落实"
STARTED_WORD = r"部分|进行中|负责人准备中|已提交|已申请|已发函"


def classify(raw):
    """Map a free-text status cell onto the board's six states; None when nothing matches.

    The leading words decide. A cell that starts as settled but still names something
    pending counts as in progress. Quoted speech, file paths and the bracket after a rule
    id are ignored, because they mention pending things that are not this row's own state.
    """
    text = plain(raw)
    text = re.sub(r"「[^」]*」|“[^”]*”|(?:docs|规划|design)/[^\s，；。（）]+\.md|(?:BR|CAP)-[A-Z]+-\d+（[^）]*）", "", text)
    text = re.sub(r"\A[①-⑳\s]+", "", text)
    if not text or text in ("—", "-"):
        return None
    if re.fullmatch(r"(?:\d{4}-)?\d{1,2}-\d{1,2}", strip_parens(text).strip()):
        return "done"                 # 06: a finished row has its status replaced by the date
    pending = re.search(OPEN_WORD, text)
    if re.match(OPEN_WORD, text):
        return "open"
    if re.match(VOID_WORD, text) or "转入" in text and not re.match(DONE_WORD, text):
        return "in_progress" if pending else "void"
    if re.match(STARTED_WORD, text):
        return "in_progress"
    if re.match(r"后续候选|可选|后续接入|P[12](?![0-9])", text):
        return "deferred"
    if re.match(r"被阻塞", text):
        return "blocked"
    # Settled words count at the start (after a short lead-in) or anywhere outside brackets.
    if re.match(rf"\S{{0,4}}(?:{DONE_WORD})", text) or re.search(DONE_WORD, strip_parens(text)):
        return "in_progress" if pending else "done"
    return "open" if pending else None


VERDICTS = (("不再处理", "void"), ("部分", "in_progress"), ("未处理", "open"), ("已按默认处理", "done"),
            ("已处理", "done"), ("已结案", "done"), ("已关闭", "done"))


def verdict(raw):
    """Status of a 'verdict (who confirmed): what was changed' cell: only the verdict counts.

    The account that follows the verdict routinely names things still pending elsewhere, so
    it is not searched; a verdict qualified as '（待…确认）' is still waiting for someone.
    """
    text = plain(raw)
    for word, status in VERDICTS:
        if text.startswith(word):
            waiting = status == "done" and re.match(r"[（(]待", text[len(word):])
            closed_later = re.search(r"[；;]\s*(?:已处理|已结案|已关闭)", text)
            return "in_progress" if waiting and not closed_later else status
    return classify(raw)


def due_date(text, weeks):
    """The deadline a cell opens with: a month-day date, or the end of the week it names.

    Brackets are dropped first; they hold remarks such as the day a note was added.
    """
    text = strip_parens(plain(text))
    explicit = re.search(r"(?<![A-Za-z\d-])(?:(\d{4})-)?(\d{1,2})-(\d{2})(?![\d-])", text)   # not the 14 of B2-14
    week = re.search(r"W(\d+)", text)
    if explicit and (not week or explicit.start() < week.start()):
        try:
            return date(int(explicit.group(1) or YEAR), int(explicit.group(2)), int(explicit.group(3)))
        except ValueError:
            pass
    if week:
        for item in weeks:
            if item["number"] == int(week.group(1)):
                return date.fromisoformat(item["end"])
    return None


class Items:
    """Collects open-item cards and keeps their ids unique."""

    def __init__(self, weeks, today):
        self.weeks = weeks
        self.today = today
        self.items = []
        self.unclassified = []
        self.seen = {}

    def add(self, ident, kind, group, title, status_raw, path, line, *, status=None, due="", owner="",
            fields=(), tracked=True, quoted=None):
        """quoted: whether status_raw is the document's own wording (default: when it was classified here)."""
        if quoted is None:
            quoted = tracked and status is None
        if status is None:
            status = classify(status_raw) if tracked else "open"
            if status is None:
                self.unclassified.append(f"{rel(path)}:{line} {ident}「{clip(status_raw, 40)}」")
                status = "open"
        self.seen[ident] = self.seen.get(ident, 0) + 1
        if self.seen[ident] > 1:
            ident = f"{ident} ·{self.seen[ident]}"
        day = due_date(due, self.weeks) if due else None
        on_hold = re.search(r"暂缓|保持待定|负责人准备中|负责人统一准备", plain(due) + plain(status_raw))
        self.items.append({
            "id": ident, "kind": kind, "group": group, "title": title,
            "status": status, "status_raw": status_raw if tracked else "未登记（这张表没有状态列）",
            "status_quoted": quoted,
            "tracked": tracked, "due": plain(due), "due_short": clip(strip_parens(plain(due)) or plain(due), 16),
            "due_date": day.isoformat() if day else None,
            "overdue": bool(tracked and day and day < self.today and not on_hold
                            and status in ("open", "in_progress", "blocked")),
            "owner": owner, "fields": [[name, text] for name, text in fields if plain(text) not in ("", "—", "-")],
            "src": source(path, line),
        })
        return self.items[-1]


def buckets(statuses):
    counts = {}
    for status in statuses:
        counts[status] = counts.get(status, 0) + 1
    return {key: counts[key] for key in STATUSES if counts.get(key)}


def dimension(key, title, src, counts, note="", labels=None, rate=True):
    """One bar of the planning overview. Deferred and void rows stay out of the percentage.

    rate=False leaves the percentage out where the source says its own statuses lag behind.
    """
    base = sum(counts.get(name, 0) for name in ("done", "in_progress", "open", "blocked"))
    return {
        "key": key, "title": title, "source": src, "buckets": counts, "labels": labels or {},
        "total": sum(counts.values()), "pct": round(counts.get("done", 0) * 100 / base) if base and rate else None,
        "note": note,
    }



# ---------------------------------------------------------------- 规划文档：未决项与完成度

DOC_PENDING = PLAN / "06_待补信息清单.md"
DOC_ACCEPT = PLAN / "10_首个完整流程验收用例.md"
DOC_DESIGN = ROOT / "design" / "README.md"
KINDS = [
    ("decision", "待拍板 / 待确认"), ("account", "账号与资质"), ("external", "外部书面答复"),
    ("material", "数据、素材与设备"), ("legal", "法务文本"), ("validation", "规则待平台验证"),
    ("doc", "文档同步"),
]
PENDING_SECTIONS = [
    # heading pattern, kind, short name used in ids of numbered rows, who acts
    (r"A\. ", "decision", "", "负责人"),
    (r"功能对照待确认", "decision", "", "负责人"),
    (r"客服代办核验待确认", "decision", "客服代办核验", "负责人"),
    (r"设计方向第三轮待确认", "decision", "设计方向第三轮", "负责人"),
    (r"分享赚与范围调整待确认", "decision", "分享赚与范围调整", "负责人"),
    (r"设计审查待确认", "decision", "设计审查", "负责人"),
    (r"C\. ", "account", "", "负责人"),
    (r"D\. ", "material", "", "负责人"),
    (r"F\. ", "legal", "", "负责人 / 法务"),
    (r"G\. ", "external", "", "负责人向对方发函"),
    (r"H\. ", "material", "", "负责人"),
]
PENDING_SKIPPED = r"E\. "            # brand deliverables: design/README.md lists them with a status
PENDING_UNTRACKED = ("material", "legal", "external")   # their tables never had a status column


def exact(table, name):
    return table.header.index(name) if name in table.header else None


def row_fields(table, cells, skip):
    return [(table.header[at], cells[at]) for at in range(min(len(cells), len(table.header))) if at not in skip]


def parse_pending(items, warn):
    """规划/06：每张带编号的表一行一张卡；没有状态列的表按未登记处理。"""
    found = set()
    for table in tables(DOC_PENDING):
        section = table.headings[1] if len(table.headings) > 1 else ""
        if len(table.headings) != 2 or table.header[0] not in ("#", "题号") or re.match(PENDING_SKIPPED, section):
            continue
        rule = next((item for item in PENDING_SECTIONS if re.search(item[0], section)), None)
        if rule:
            found.add(rule[0])
        elif "待确认" in section:     # sections of this kind keep being added; take them as they come
            short = re.sub(r"\d{4}-\d{2}-\d{2}|待确认", "", strip_parens(section)).strip()
            rule = (section, "decision", short, "负责人")
        else:
            warn(f"06「{section}」有一张带编号的表没有纳入看板（第 {table.line} 行）")
            continue
        _, kind, short, default_owner = rule
        status_at, due_at = exact(table, "状态"), exact(table, "截止")
        if status_at is None and kind not in PENDING_UNTRACKED:
            warn(f"06「{section}」的表没有「状态」列（第 {table.line} 行），这 {len(table.rows)} 行按未登记计")
        for line, cells in table.rows:
            first = plain(cells[0])
            if not first:
                continue
            ident = f"{short} #{first}" if first.isdigit() else clip(strip_parens(first) or first, 28)
            title = f"{plain(cells[1])}：{cells[2]}" if table.header[1] == "对象" else cells[1]
            status = cells[status_at] if status_at is not None else ""
            due = cells[due_at] if due_at is not None else ""
            tracked = status_at is not None
            if not tracked and re.match(STARTED_WORD, plain(due)):
                status, due, tracked = due, "", True      # a status written into the deadline cell
            role = re.match(r"待(契约线|运营|法务|财务)", plain(status))
            # A partly settled row whose remaining part names someone else is no longer the owner's.
            text = plain(status)
            rest = re.search(r"(?:待|由)(法务|财务|运营|契约线|实测)|(法务|财务|运营|契约线)确认仍待", text)
            if not role and rest and classify(status) == "in_progress" and not re.search(r"待负责人|仍未定", text):
                role = rest
            item = items.add(ident, kind, f"06 {section}", title, status, DOC_PENDING, line, due=due,
                             owner=next(filter(None, role.groups())) if role else default_owner, tracked=tracked,
                             fields=row_fields(table, cells, {0, 1, status_at, due_at}))
            if not tracked and kind == "legal":
                item["status_raw"] = "未登记（06 写明负责人称法务文本已基本完成，只是没有逐项标记）"
    missing = [rule[0] for rule in PENDING_SECTIONS if rule[0] not in found]
    if missing:
        warn("06 里没有读到这些小节的表：" + "、".join(text.replace("\\", "").strip() for text in missing))


RULE_STATUS = (("已确认", "done"), ("默认假设", "in_progress"), ("待决策", "open"), ("待验证", "blocked"), ("废弃", "void"))
RULE_LABELS = {"done": "已确认", "in_progress": "默认假设（按默认值开发）", "open": "待决策", "blocked": "待平台验证", "void": "废弃"}


def parse_rules(items, warn):
    """规划/08：README 索引给出全部条目的状态；14、15 给出要人处理的那部分。"""
    index = next((table for table in tables(RULES / "README.md") if table.header[:3] == ["编号", "标题", "状态"]), None)
    statuses = []
    for _, cells in index.rows if index else []:
        status = next((value for prefix, value in RULE_STATUS if plain(cells[2]).startswith(prefix)), None)
        if status:
            statuses.append(status)
    if not statuses:
        warn("08 README 的规则索引表没有读到（表头应为「编号 | 标题 | 状态 | 所在文件」）")

    decisions = RULES / "14_待决策汇总.md"
    conflicts = []
    read = dict.fromkeys(("14.1", "14.3", "14.5", "15.1"), 0)
    for table in tables(decisions):
        section = table.section
        if section.startswith("14.1") and table.header[0] == "编号":
            owner_at, due_at = table.column("负责人"), table.column("最晚")
            for line, cells in table.rows:
                read["14.1"] += 1
                items.add(plain(cells[0]), "decision", "08 §14.1 规则待决策", cells[1], "待决策（已按默认值写成配置或开关）",
                          decisions, line, status="open", due=cells[due_at] if due_at else "",
                          owner=plain(cells[owner_at]) if owner_at else "", fields=row_fields(table, cells, {0, 1, owner_at, due_at}))
        elif section.startswith("14.3") and "处理状态" in table.header:
            at, owner_at = table.header.index("处理状态"), table.column("决策人")
            for line, cells in table.rows:
                read["14.3"] += 1
                status = verdict(cells[at]) or "open"
                conflicts.append(status)
                if status != "done":
                    items.add(plain(cells[0]), "decision", "08 §14.3 跨主题分歧", cells[1], cells[at], decisions, line,
                              status=status, quoted=True, owner=plain(cells[owner_at]) if owner_at else "",
                              fields=row_fields(table, cells, {0, 1, owner_at, at}))
        elif section.startswith("14.5") and table.header[0] == "G 编号":
            owner_at, due_at = table.column("决策人"), table.column("最晚")
            for line, cells in table.rows:
                read["14.5"] += 1
                items.add(f"规则缺口 {plain(cells[0])}", "decision", "08 §14.5 规则缺口的默认处理", cells[2],
                          "已按默认处理，待确认", decisions, line, status="in_progress", due=cells[due_at] if due_at else "",
                          owner=plain(cells[owner_at]) if owner_at else "", fields=row_fields(table, cells, {0, 2, owner_at, due_at}))
    pending = RULES / "15_待验证汇总.md"
    for table in tables(pending):
        if table.section.startswith("15.1") and table.header[0] == "编号":
            for line, cells in table.rows:
                read["15.1"] += 1
                items.add(plain(cells[0]), "validation", "08 §15.1 规则待平台验证", cells[1],
                          "待验证（能力验证通过前按默认值开发，不对用户承诺）", pending, line, status="blocked",
                          owner="随 09 能力验证", fields=row_fields(table, cells, {0, 1}))
    unread = [section for section, count in read.items() if not count]
    if unread:
        warn("08 的这些小节没有读到表（小节号或表头变了）：§" + "、§".join(unread))
    return statuses, conflicts


CAP_STATUS = {"未开始": "open", "进行中": "in_progress", "支持": "done", "部分支持": "done", "不支持": "done", "被阻塞": "blocked"}
CAP_LABELS = {"done": "已有结论", "in_progress": "进行中", "open": "未开始", "blocked": "被阻塞", "deferred": "后续（首版不要求）"}
PLATFORMS = [("TB", "淘宝"), ("JD", "京东"), ("PDD", "拼多多"), ("X", "跨平台与系统"), ("MT", "美团")]


def parse_caps(warn):
    """规划/09：各平台主表的「状态」列是唯一状态来源；验证计划没有状态列。"""
    caps = []
    for path in DOCS.glob(CAPS, "[0-9]*.md"):
        for table in tables(path):
            if table.header[:2] != ["编号", "能力"] or "状态" not in table.header:
                continue
            at = table.header.index("状态")
            cell_at = lambda cells, name: cells[table.header.index(name)] if name in table.header else ""
            whole_later = re.search(r"P[12](?![0-9])", " ".join(table.headings))   # 美团: the file itself is P1
            for line, cells in table.rows:
                ident = re.fullmatch(r"CAP-([A-Z]+)-(\d{2})", plain(cells[0]))
                if not ident:
                    continue
                raw = plain(cells[at])
                status = next((value for prefix, value in sorted(CAP_STATUS.items(), key=lambda pair: -len(pair[0]))
                               if raw.startswith(prefix)), "open")
                due = plain(cell_at(cells, "截止"))
                later = whole_later or re.match(r"P[12](?![0-9])|后续接入|未排期", due) or re.search(r"(选定|开通|批下|签约)后", due)
                if status == "open" and later:
                    status = "deferred"
                caps.append({
                    "id": ident.group(0), "platform": ident.group(1), "number": ident.group(2),
                    "platform_name": dict(PLATFORMS).get(ident.group(1), ident.group(1)),
                    "title": cells[1], "short": clip(re.split(r"[：:（(]", plain(cells[1]), maxsplit=1)[0], 22),
                    "status": status, "status_raw": raw, "due": due, "owner": plain(cell_at(cells, "负责人")),
                    "fields": row_fields(table, cells, {0, 1, at, len(table.header) - 1, len(table.header) - 2}),
                    "src": source(path, line),
                })
    unread = [name for platform, name in PLATFORMS if not any(cap["platform"] == platform for cap in caps)]
    if unread:
        warn("09 没有读到这些平台的主表（表头应以「编号 | 能力」开头并含「状态」列）：" + "、".join(unread))
    vtasks = []
    readme = CAPS / "README.md"
    for table in tables(readme):
        if table.header[:3] != ["编号", "任务", "CAP"]:
            continue
        week = re.match(r"[\d.]+\s+([A-Z][A-Z0-9–]*)", table.section)
        for line, cells in table.rows:
            if not re.fullmatch(r"V-\d+", plain(cells[0])):
                continue
            cell = lambda at: cells[at] if at < len(cells) else ""
            vtasks.append({
                "id": plain(cells[0]), "week": week.group(1) if week else "", "title": cells[1], "caps": plain(cells[2]),
                "owner": plain(cell(4)), "blocks": plain(cell(5)), "done_mark": "文档没有记录这项是否完成",
                "fields": [["依赖", cell(3)], ["完成标志", cell(6)]], "src": source(readme, line),
            })
    if not vtasks:
        warn("09 README §7 验证计划的表没有读到（表头应为「编号 | 任务 | CAP | …」）")
    conflicts = []
    names = {}
    for table in tables(readme):
        if table.section.startswith("附录 A") and "处理状态" in table.header:
            at = table.header.index("处理状态")
            conflicts = [(line, cells, verdict(cells[at]) or "open", at) for line, cells in table.rows]
        for _, cells in table.rows:
            if plain(cells[0]) == "三家同号同义":       # the README's own names for the shared numbers
                names = dict(re.findall(r"`(\d{2})`\s*([^、`|]+)", cells[1]))
    if not conflicts:
        warn("09 README 附录 A 的冲突表没有读到（表头应含「处理状态」列）")
    return caps, vtasks, conflicts, names


def parse_acceptance(warn):
    """规划/10：验收用例条数（写好的），以及 §6.1 规则缺口的处理状态。"""
    cases = {}
    gaps = []
    for table in tables(DOC_ACCEPT):
        if table.header[:3] == ["编号", "目标", "Given"]:
            cap_at = exact(table, "CAP")
            for _, cells in table.rows:
                ident = re.match(r"AC-(S\d)-\d+", plain(cells[0]))
                if not ident:
                    continue
                stage = cases.setdefault(ident.group(1), {"total": 0, "must": 0, "void": 0})
                if re.match(r"[（(]作废|已作废|作废(?:[（(：:；;。]|\s*$)", plain(cells[1])):
                    stage["void"] += 1
                    continue
                stage["total"] += 1
                stage["must"] += cap_at is not None and plain(cells[cap_at]).startswith("—")
        elif "处理状态" in table.header and table.header[0] == "编号":
            at = table.header.index("处理状态")
            gaps = [verdict(cells[at]) or "open" for _, cells in table.rows]
    if not cases:
        warn("10 的验收用例表没有读到（表头应以「编号 | 目标 | Given」开头）")
    if not gaps:
        warn("10 §6.1 的规则缺口表没有读到（表头应含「处理状态」列）")
    return cases, gaps


def parse_decisions(items, warn):
    """规划/00 §3：已定的决策，与仍按默认、等确认的决策。"""
    settled = 0
    pending = 0
    for table in tables(DOC_OVERVIEW):
        if table.section.startswith("3.1") and table.header[:2] == ["#", "决策"]:
            settled = len(table.rows)
        elif table.section.startswith("3.2"):
            due_at = exact(table, "截止")
            if table.header[0] != "#":
                warn(f"00 §3.2 的表头变了（第 {table.line} 行，首列应为「#」），默认决策没有读到")
                continue
            for line, cells in table.rows:
                pending += 1
                first = plain(cells[0])
                ident = first if re.fullmatch(r"D\d+", first) else f"00 §3.2 #{pending}"
                due = cells[due_at] if due_at is not None else ""
                confirmed = re.search(r"已确认", plain(due))      # the deadline cell records a later confirmation
                items.add(ident, "decision", "00 §3.2 默认决策，待确认或推翻", cells[1],
                          plain(due) if confirmed else "按默认执行，待负责人确认或推翻", DOC_OVERVIEW, line,
                          status="done" if confirmed else "open", quoted=bool(confirmed), due="" if confirmed else due,
                          owner="负责人", fields=row_fields(table, cells, {0, 1, due_at}))
    if not settled:
        warn("00 §3.1 已定决策表没有读到（表头应为「# | 决策 | 影响」）")
    scope = {}
    for table in tables(DOC_OVERVIEW):
        if table.header[:3] == ["域", "功能", "阶段"]:
            for _, cells in table.rows:
                stage = plain(cells[2])
                unsettled = "待定" in stage or "待确认" in plain(cells[0])
                key = "open" if unsettled else "deferred" if re.match(r"P[12]|后续接入", stage) else "done"
                scope[key] = scope.get(key, 0) + 1
    return settled, pending, scope


def parse_design(items, warn):
    """design/README.md 的素材清单。"""
    statuses = []
    for table in tables(DOC_DESIGN):
        if table.header[:2] != ["#", "事项"] or "状态" not in table.header:
            continue
        at, due_at = table.header.index("状态"), exact(table, "截止")
        for line, cells in table.rows:
            raw = cells[at] if at < len(cells) else ""
            status = "void" if re.search(r"不再", plain(raw)[:24]) else None
            item = items.add(f"设计素材 #{plain(cells[0])}", "material", "design/README 素材清单", cells[1], raw, DOC_DESIGN,
                             line, status=status, quoted=True, due=cells[due_at] if due_at is not None else "", owner="负责人",
                             fields=row_fields(table, cells, {0, 1, at, due_at}))
            statuses.append(item["status"])
    if not statuses:
        warn("design/README.md 的素材清单表没有读到（表头应为「# | 事项 | … | 状态」）")
    return statuses



def parse_diagram_gaps(items, warn):
    """规划/12 §9：画图时发现的不一致。类别列以「已关闭 / 部分关闭」开头的才算处理过。"""
    path = PLAN / "12_关键流程与状态图.md"
    statuses = []
    for table in tables(path):
        if len(table.headings) < 2 or not table.headings[1].startswith("9.") or table.header[0] != "编号":
            continue
        if "类别" not in table.header:
            warn(f"12 §{table.section} 的表没有「类别」列（第 {table.line} 行），这张表没有读")
            continue
        at = table.header.index("类别")
        for line, cells in table.rows:
            if not re.fullmatch(r"[A-Z]-\d{2}", plain(cells[0])):
                continue
            category = plain(cells[at])
            status = verdict(category) if re.match(r"已关闭|部分关闭", category) else "open"
            statuses.append(status)
            if status != "done":
                note, _, origin = category.rpartition("｜原类别：")
                # Partly closed rows say in the note whether the owner's part is still open.
                owner_choice = "负责人选择" in origin and (status == "open" or bool(re.search(r"负责人选|待负责人", note)))
                items.add(f"12-{plain(cells[0])}", "decision" if owner_choice else "doc", f"12 §{table.section}（状态取自「类别」列）",
                          clip(cells[1], 90), category, path, line, status=status, quoted=True,
                          owner="负责人选择" if owner_choice else "代理同步或实测",
                          fields=[("不一致或缺口", cells[1]), ("位置", cells[2]), ("保守默认", cells[3])])
    if not statuses:
        warn("12 §9 的不一致清单没有读到（表头应含「类别」列）")
    return statuses


def parse_requirements(warn):
    """规划/01：需求条目按阶段分，近期的算写好，远期只列目标。"""
    counts = {}
    for table in tables(PLAN / "01_需求规划.md"):
        at = exact(table, "阶段")
        numbered = [line for line, cells in table.rows if re.match(r"~*F-[A-Z0-9]+-\d+", plain(cells[0]))]
        if at is None or table.header[0] != "编号":
            if numbered and table.header[0] == "编号":
                warn(f"01 第 {table.line} 行的需求表没有「阶段」列，{len(numbered)} 条需求没有计入")
            continue
        for line, cells in table.rows:
            if line not in numbered:
                continue
            stage = plain(cells[at])
            key = ("void" if stage.startswith("作废") else "open" if stage.startswith("待立项")
                   else "deferred" if re.match(r"P[12]|后续接入", stage) else "done")
            counts[key] = counts.get(key, 0) + 1
    if not counts:
        warn("01 的需求表没有读到（表头应为「编号 | 需求 | 阶段 | …」）")
    return {key: counts[key] for key in STATUSES if counts.get(key)}


def parse_approvals(warn):
    """规划/11 §7.3 批准栏。"""
    for table in tables(PLAN / "11_开发协作与自主推进.md"):
        if table.section.startswith("7.3") and "状态" in table.header:
            at = table.header.index("状态")
            return buckets("done" if plain(cells[at]).startswith("已确认") else "open" for _, cells in table.rows)
    warn("11 §7.3 批准栏没有读到")
    return {}


# ---------------------------------------------------------------- 组装

def build(board, version, plan_ref):
    warnings = []
    warn = warnings.append
    now = datetime.now(TZ)
    today = now.date()
    moment = lambda stamp: datetime.fromtimestamp(stamp, TZ).strftime("%m-%d %H:%M")
    clock = lambda at: at.strftime("%H:%M:%S") if at else None
    if plan_ref:
        planning = {"mode": "git", "ref": REF_LABEL.get(plan_ref[0], plan_ref[0]), "sha": plan_ref[1][:7],
                    "committed_at": moment(plan_ref[2]), "fetched_at": clock(board.plan.fetch_at),
                    "note": board.plan.fetch_error}
    else:
        planning = {"mode": "local", "root": str(ROOT), "branch": git_text(ROOT, "rev-parse", "--abbrev-ref", "HEAD"),
                    "sha": git_text(ROOT, "rev-parse", "--short", "HEAD"),
                    "dirty": bool(git_text(ROOT, "status", "--porcelain", "--", "规划", "design/README.md"))}
        if not board.local:
            warn("规划仓库里找不到 main 的提交，改读脚本旁边的本机文件")

    def read(label, default, parse, *args):
        """Run one parser; a source it cannot cope with costs that part of the board, not all of it."""
        try:
            return parse(*args)
        except Exception as error:
            warn(f"{label}解析出错（{type(error).__name__}: {error}），这一部分没有显示")
            return default

    for name, repo in (("规划仓库", board.plan), ("代码仓库", board.code)):
        if repo.fetch_error:
            warn(f"{name}{repo.fetch_error}，数据可能落后")
    if plan_ref and plan_ref[0] == "HEAD":
        warn("规划仓库没有远端 main 的引用，读的是本地检出的提交，可能落后或含未合并的内容")
    weeks = read("05 周计划", [], parse_weeks, warn)
    stages = read("05 阶段表", [], parse_stages, warn)
    tasks = read("05 任务表", [], parse_tasks, warn)
    stage_of = {}
    for stage in stages:
        for ident in stage["task_ids"]:
            stage_of.setdefault(ident, []).append(stage["id"])
    current = next((week for week in weeks if week["start"] <= today.isoformat() <= week["end"]), None)
    last = max(weeks, key=lambda week: week["number"], default=None)
    # Past the last planned week every dated task is behind, not none of them.
    week_now = current["number"] if current else last["number"] + 1 if last and today.isoformat() > last["end"] else None

    code = board.code
    ledger = {"available": code.available, "repo": str(code.path), "entries": []}
    metrics = {}
    merged = {}
    if code.available:
        found = code.ref()
        if found:
            name, sha, stamp = found
            ledger.update(ref=REF_LABEL.get(name, name), sha=sha[:7], web_url=code.web_url(),
                          committed_at=moment(stamp), fetched_at=clock(code.fetch_at), note=code.fetch_error)
            ledger["entries"] = code.ledger(sha)
            metrics = code_metrics(code, sha, plan_ref[1] if plan_ref else "HEAD")
            if name == "HEAD":
                warn("代码仓库没有远端 main 的引用，台账读的是本地检出，可能落后或含未合并的内容")
            else:
                merged = merged_titles(code, sha)
            if not ledger["entries"]:
                warn(f"代码仓库 {ledger['ref']} 上没有读到 ops/tasks 台账")
        else:
            ledger["available"] = False
    inflight = read("运行目录", {}, read_inflight, board.runs)
    orphans = read("台账合并", [], join_ledger, tasks, ledger["entries"], inflight, merged, warn)
    for task in tasks:
        task["stages"] = stage_of.get(task["id"], [])
        task["behind"] = bool(week_now is not None and task["week_last"] is not None and task["week_last"] < week_now
                              and task["state"] in ("planned", "todo", "in_progress"))

    items = Items(weeks, today)
    settled, pending, scope = read("00 决策与范围", (0, 0, {}), parse_decisions, items, warn)
    read("06 待补信息", None, parse_pending, items, warn)
    rule_statuses, conflict_statuses = read("08 业务规则", ([], []), parse_rules, items, warn)
    caps, vtasks, cap_conflicts, cap_names = read("09 平台能力", ([], [], [], {}), parse_caps, warn)
    for line, cells, status, at in cap_conflicts:
        if status in ("open", "in_progress") and len(cells) >= 5:
            items.add(f"09-{plain(cells[0])}", "doc", "09 附录 A 需回写其他文档的冲突", cells[1], cells[at],
                      CAPS / "README.md", line, status=status, quoted=True, owner="代理同步",
                      fields=[("所在文档", cells[2]), ("建议", cells[3]), ("依据", cells[4])])
    cases, gap_statuses = read("10 验收用例", ({}, []), parse_acceptance, warn)
    design_statuses = read("design 素材清单", [], parse_design, items, warn)
    diagram_statuses = read("12 不一致清单", [], parse_diagram_gaps, items, warn)
    requirement_counts = read("01 需求", {}, parse_requirements, warn)
    approvals = read("11 批准栏", {}, parse_approvals, warn)
    # Notes are worth a look but do not mean a table went unread; --check stays at exit 0 for them.
    notes = [f"状态写法没能归类，暂按待办计：{text}" for text in items.unclassified] + list(short_rows())
    if not ledger["available"]:
        notes.append(f"没有读到工程台账（{ledger['repo']}），开发状态未知")
    kind_label = dict(KINDS)
    listed = {item["id"] for item in items.items if item["group"].startswith("08 §14.1")}
    for item in items.items:
        item["kind_label"] = kind_label[item["kind"]]
        if item["kind"] in ("account", "legal"):
            item["overdue"] = False   # 06 says these are largely done but not ticked off row by row
        # 06 and 08 §14.1 both list a few decisions; keep both cards, count the decision once.
        same = re.search(r"(BR-[A-Z]+-\d+)（待决策", " ".join(text for _, text in item["fields"]))
        if item["group"].startswith("06 ") and same and same.group(1) in listed:
            item["same_as"] = same.group(1)
    active = ("open", "in_progress", "blocked")

    def of(*groups):
        return [item for item in items.items if item["group"].startswith(groups)]

    confirm = [item for item in of("06 ") if item["kind"] == "decision"]
    account = [item for item in of("06 ") if item["kind"] == "account"]
    untracked = [item for item in items.items if not item["tracked"]]
    schedule = buckets(
        task["plan_state"] if task["plan_state"] != "active" else "done" if task["weeks"]
        else "open" if task["when"].startswith("待排") else "in_progress" for task in tasks)
    cap_counts = buckets(cap["status"] for cap in caps)
    case_total = sum(stage["total"] for stage in cases.values())
    case_void = sum(stage["void"] for stage in cases.values())
    dimensions = [
        dimension("decisions", "产品决策", "规划/00 §3", {"done": settled, **({"open": pending} if pending else {})},
                  "§3.1 已定的决策对 §3.2 仍按默认、等确认或推翻的决策。", {"open": "按默认，待确认"}),
        dimension("scope", "范围裁决", "规划/00 §4", {key: scope[key] for key in STATUSES if scope.get(key)},
                  "已定 = 阶段已写明（内测、公开、不做等）；远期 = P1、P2 与后续接入；待办 = 里程碑待定。", {"done": "已定"}),
        dimension("requirements", "需求条目", "规划/01", requirement_counts,
                  "近期阶段的需求已写成条目；P1、P2 按约定只写目标。", {"done": "近期已写", "open": "待立项"}),
        dimension("rules", "业务规则", "规划/08 规则索引", buckets(rule_statuses),
                  "默认假设与待决策都已有默认值，可以照着开发；百分比只算负责人已确认的。", RULE_LABELS),
        dimension("conflicts", "规则之间的分歧", "规划/08 §14.3", buckets(conflict_statuses),
                  "进行中 = 已按默认处理，等法务或财务确认。", {"done": "已结案", "in_progress": "已按默认处理，待确认"}),
        dimension("gaps", "验收用例暴露的规则缺口", "规划/10 §6.1", buckets(gap_statuses),
                  f"验收用例共 {case_total} 条（" + "、".join(f"{key} {value['total']}" for key, value in sorted(cases.items()))
                  + f"），其中必过项 {sum(stage['must'] for stage in cases.values())} 条"
                  + (f"；另有 {case_void} 条已作废，没有计入。" if case_void else "。"),
                  {"done": "已处理", "in_progress": "已按默认处理，待确认"}),
        dimension("diagrams", "画流程图时发现的不一致", "规划/12 §9", buckets(diagram_statuses),
                  "多数是文档之间要同步的地方，少数要实测或负责人选择。",
                  {"done": "已关闭", "in_progress": "部分关闭", "open": "未关闭"}),
        dimension("confirm", "等负责人确认的事项", "规划/06 A 节与各「待确认」节", buckets(item["status"] for item in confirm),
                  "这些都已按默认做法写进规划，不确认也能照着开发；确认后才算定下来。",
                  {"done": "已定", "in_progress": "部分已定", "open": "待确认", "deferred": "后续", "void": "已取消或转出"}),
        dimension("account", "账号、资质与权限", "规划/06 C 节", buckets(item["status"] for item in account),
                  "06 写明负责人称这部分已基本完成，只是没有逐项标记；这里按表内文字统计，所以不算百分比。",
                  {"open": "表内仍写待办"}, rate=False),
        dimension("caps", "平台能力验证", "规划/09 各平台主表", cap_counts,
                  "实验设计、通过标准与降级方案都已写好；这里统计的是实测有没有结论。结论要调度人签字才算。", CAP_LABELS),
        dimension("cap_conflicts", "能力验证发现的文档冲突", "规划/09 附录 A",
                  buckets(status for _, _, status, _ in cap_conflicts), "", {"done": "已处理", "in_progress": "部分处理", "open": "未处理", "void": "不再处理"}),
        dimension("design", "品牌与设计素材", "design/README.md 清单", buckets(design_statuses), ""),
        dimension("schedule", "任务排期", "规划/05 §3", schedule,
                  "05 §1 写明后面几周的周次要在复盘后重排，现有周次不能用来推断进度，所以不算百分比。",
                  {"done": "已排周次", "in_progress": "随其他任务触发", "open": "待排", "deferred": "P1 / 未排期"}, rate=False),
        dimension("approvals", "协作规则的批准栏", "规划/11 §7.3", approvals, "", {"done": "已确认", "open": "待确认"}),
    ]

    parents = [task for task in tasks if task["plan_state"] == "active"]
    split = [task for task in parents if task["ledger"]]
    subs = [entry for task in tasks for entry in task["ledger"]]
    undecided = [item for item in items.items
                 if item["kind"] == "decision" and item["status"] in active and not item.get("same_as")]
    owner_open = [item for item in undecided if item["owner"].startswith("负责人")]
    others_open = len(undecided) - len(owner_open)
    concluded = sum(cap["status"] == "done" for cap in caps)
    scoped = sum(cap["status"] != "deferred" for cap in caps)
    confirmed = sum(status == "done" for status in rule_statuses)
    live_rules = sum(status != "void" for status in rule_statuses)
    operations = metrics.get("operations")
    headline = [
        {"label": "业务规则：负责人已确认", "value": f"{confirmed}", "unit": f"/ {live_rules} 条",
         "hint": f"其余 {live_rules - confirmed} 条按默认值开发（默认假设、待决策、待平台验证）"},
        {"label": "等负责人拍板或确认", "value": f"{len(owner_open)}", "unit": "项",
         "hint": "按条目计：00 §3.2、06 各待确认节、08 待决策与分歧、12 里要负责人选择的不一致"
                 + (f"；另有 {others_open} 项等法务、财务、运营或契约线" if others_open else "")},
        {"label": "平台能力验证：已有结论", "value": f"{concluded}", "unit": f"/ {scoped} 条",
         "hint": f"进行中 {cap_counts.get('in_progress', 0)} 条；另有 {cap_counts.get('deferred', 0)} 条首版不要求"},
        {"label": "开发进度（不属于规划）", "value": f"{len(split)}", "unit": f"/ {len(parents)} 个任务已拆入台账",
         "hint": f"台账拆分 {sum(entry['state'] == 'done' for entry in subs)} / {len(subs)} 已合并"
                 + (f"；接口 {operations['total'] - operations['planned']} / {operations['total']} 已实现" if operations else "")
                 + f"；验收记录 {metrics.get('acceptance', {}).get('rows', 0)} 条"}
        if ledger["available"] else
        {"label": "开发进度（不属于规划）", "value": "—", "unit": "读不到工程台账",
         "hint": "没有找到代码仓库或它的主干，开发状态未知"},
    ]

    def states(group):
        return tally(group, "state")

    def progress(group):
        """How many of a group's tasks have any ledger entry; the ledger cannot say how many are finished."""
        return {"total": len(group), "states": states(group),
                "started": sum(task["state"] in ("in_progress", "merged") for task in group)}

    lines = [{"id": line, "name": LINE_NAMES[line], **progress([task for task in tasks if task["line"] == line])}
             for line in LINES]
    stage_rows = [{"id": stage["id"], "name": stage["name"], "result": stage["result"], "weeks": stage["weeks"],
                   **progress([task for task in tasks if stage["id"] in task["stages"]])} for stage in stages]
    matrix = [platform for platform, _ in PLATFORMS if platform != "X"]
    names = dict(cap_names)
    for cap in caps:
        if cap["platform"] in matrix:
            names.setdefault(cap["number"], cap["short"])
    spec = metrics.get("spec_ref") or {}

    return {
        "version": version, "generated_at": now.isoformat(timespec="seconds"), "today": today.isoformat(),
        "warnings": warnings, "notes": notes,
        "sources": {
            "planning": planning,
            "ledger": {key: value for key, value in ledger.items() if key != "entries"},
            "runs": {"available": board.runs.is_dir(), "dir": str(board.runs)},
            "spec_ref": spec,
        },
        "calendar": {
            "weeks": [{key: week[key] for key in ("id", "number", "range", "start", "end")} for week in weeks],
            "current_week": current["id"] if current else None,
            "milestones": read("00 里程碑", [], parse_milestones, weeks, today, warn),
            "note": "日期是当前计划，随外部资料、验证与开发进度调整（00 §5）。",
        },
        "planning": {
            "lede": "统计的是规划文档自己收口到什么程度：决定定了没有、规则确认了没有、要补的资料到了没有。"
                    "规划写完不等于开发完成，也不等于已验收；开发进度看下面的「各线开发任务」。"
                    "百分比 = 已完成 ÷（已完成 + 进行中 + 待办 + 被阻塞），远期与作废不计入。",
            "headline": headline, "dimensions": [item for item in dimensions if item["total"]],
            "untracked": len(untracked),
        },
        "tasks": tasks, "lines": lines, "stages": stage_rows,
        "ledger": {"entries": ledger["entries"], "orphans": orphans, "metrics": metrics},
        "open_items": items.items,
        "item_kinds": [{"key": key, "label": label,
                        "open": sum(item["kind"] == key and item["status"] in active for item in items.items)}
                       for key, label in KINDS],
        "caps": {
            "items": caps, "vtasks": vtasks, "labels": CAP_LABELS, "names": names, "matrix": matrix,
            "platforms": [{"id": platform, "name": name, "total": sum(cap["platform"] == platform for cap in caps),
                           "buckets": buckets(cap["status"] for cap in caps if cap["platform"] == platform)}
                          for platform, name in PLATFORMS],
            "note": "状态取自各平台文件主表的「状态」列。「已有结论」指支持、部分支持或不支持，须调度人签字（09 §0.2）；"
                    "没有结论的能力不能写成对用户的承诺。",
            "vnote": "09 README §7 的验证计划没有状态列，文档里查不到每项是否做完；这里只列计划。",
        },
    }


def report(data):
    """Plain-text summary for --check."""
    planning = data["sources"]["planning"]
    origin = (f"规划仓库 {planning['ref']} @ {planning['sha']}；要检查还没合并的本机改动，加 --local"
              if planning["mode"] == "git" else f"本机文件 {planning['root']}")
    lines = [f"来源：{origin}",
             f"OK: 规划任务 {len(data['tasks'])} 个，台账拆分任务 {len(data['ledger']['entries'])} 个，"
             f"未决项 {len(data['open_items'])} 条，平台能力 {len(data['caps']['items'])} 条，"
             f"验证任务 {len(data['caps']['vtasks'])} 项"]
    for item in data["planning"]["dimensions"]:
        counts = "，".join(f"{item['labels'].get(key) or STATUS_LABEL[key]} {value}" for key, value in item["buckets"].items())
        lines.append(f"  {item['title']}（{item['source']}）：{counts}")
    for text in data["notes"]:
        lines.append(f"NOTE: {text}")
    for text in data["warnings"]:
        lines.append(f"WARN: {text}")
    return lines


# ---------------------------------------------------------------- 服务与命令行

class Board:
    """Builds the board on demand and rebuilds it only when a source changed."""

    def __init__(self, code_repo, runs_dir, local):
        self.plan = Repo(ROOT)
        self.code = Repo(code_repo)
        self.runs = Path(runs_dir)
        self.local = local
        self.lock = threading.Lock()
        self.cached = None
        self.cached_version = None
        self.version_at = 0.0
        self.version_value = None

    def planning_ref(self):
        """Commit the planning text is read from; None when it is the working tree."""
        return None if self.local else self.plan.ref()

    def watched(self):
        files = [*sorted(STATIC.glob("*")), *inflight_files(self.runs)]
        if self.local:
            files += [*sorted(PLAN.rglob("*.md")), DOC_DESIGN]
        return files

    def version(self):
        """Cheap fingerprint of every input; recomputed at most once a second."""
        now = time.monotonic()
        if self.version_value and now - self.version_at < 1.0:
            return self.version_value
        digest = hashlib.sha1()
        for path in self.watched():
            try:
                stat = path.stat()
                digest.update(f"{path}:{stat.st_mtime_ns}:{stat.st_size}\n".encode("utf-8"))
            except OSError:
                digest.update(f"{path}:missing\n".encode("utf-8"))
        ref = self.code.ref() if self.code.available else None
        clock = datetime.now(timezone.utc)
        stale = [expired(read_json(path).get("heartbeat_at"), clock, LEASE) for path in self.runs.glob("claims/*/holder.json")]
        local = (git_text(ROOT, "rev-parse", "HEAD"), git_text(ROOT, "status", "--porcelain", "--", "规划", "design/README.md")) if self.local else None
        digest.update(repr((ref, self.planning_ref(), self.plan.fetch_error, self.code.fetch_error, stale, local,
                            datetime.now(TZ).date().isoformat())).encode("utf-8"))
        self.version_value, self.version_at = digest.hexdigest()[:16], now
        return self.version_value

    def get(self):
        version = self.version()
        with self.lock:
            if self.cached_version != version:
                plan_ref = self.planning_ref()
                DOCS.use(self.plan, plan_ref[1] if plan_ref else None)
                self.cached = build(self, version, plan_ref)
                self.cached_version = version
            return self.cached

    def fetch(self):
        if not self.local:
            self.plan.fetch()
        if self.code.available:
            self.code.fetch()


def fetch_loop(board, seconds):
    while True:
        board.fetch()
        time.sleep(seconds)


STATIC_ROUTES = {
    "/": (STATIC / "index.html", "text/html; charset=utf-8"),
    "/static/kanban.css": (STATIC / "kanban.css", "text/css; charset=utf-8"),
    "/static/kanban.js": (STATIC / "kanban.js", "text/javascript; charset=utf-8"),
    "/tokens.css": (ROOT / "design" / "tokens" / "variables.css", "text/css; charset=utf-8"),
    "/logo.svg": (ROOT / "design" / "logo" / "source" / "logo-mark.svg", "image/svg+xml"),
}


def handler_for(board, hosts):
    class Handler(BaseHTTPRequestHandler):
        server_version = "couli-kanban"

        def send(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def send_json(self, data, status=200):
            self.send(status, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            # Only answer requests addressed to this machine, so another site cannot read the board.
            if self.headers.get("Host", "") not in hosts:
                return self.send(403, b"forbidden", "text/plain")
            path = urlsplit(self.path).path
            try:
                if path in STATIC_ROUTES:
                    file, content_type = STATIC_ROUTES[path]
                    return self.send(200, file.read_bytes(), content_type)
                if path == "/api/version":
                    fetched = max(filter(None, (board.plan.fetch_at, board.code.fetch_at)), default=None)
                    return self.send_json({"version": board.version(), "fetched_at": fetched and fetched.strftime("%H:%M:%S")})
                if path == "/api/board":
                    return self.send_json(board.get())
                return self.send(404, b"not found", "text/plain")
            except Exception as error:  # the page shows the message instead of a dead connection
                return self.send_json({"error": f"{type(error).__name__}: {error}"}, 500)

        do_HEAD = do_GET

        def log_message(self, *args):
            pass

    return Handler


def export_html(data):
    """One self-contained file: styles, script and data inlined, no server needed."""
    page = (STATIC / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "design" / "tokens" / "variables.css").read_text(encoding="utf-8")
    css += (STATIC / "kanban.css").read_text(encoding="utf-8")
    script = (STATIC / "kanban.js").read_text(encoding="utf-8")
    logo = (ROOT / "design" / "logo" / "source" / "logo-mark.svg").read_bytes()
    import base64
    logo_url = "data:image/svg+xml;base64," + base64.b64encode(logo).decode("ascii")
    payload = json.dumps(data, ensure_ascii=False)
    for char in ("<", "\u2028", "\u2029"):          # the text comes from many hands; keep it inert inside <script>
        payload = payload.replace(char, f"\\u{ord(char):04x}")
    page = page.replace('<link rel="stylesheet" href="tokens.css">\n', "")
    page = page.replace('<link rel="stylesheet" href="static/kanban.css">', f"<style>\n{css}</style>")
    page = page.replace('href="logo.svg"', f'href="{logo_url}"').replace('src="logo.svg"', f'src="{logo_url}"')
    page = page.replace('<script id="board-data" type="application/json"></script>',
                        f'<script id="board-data" type="application/json">{payload}</script>')
    return page.replace('<script src="static/kanban.js"></script>', f"<script>\n{script}</script>")


def main():
    if sys.version_info < (3, 9):
        print("ERROR: Python >= 3.9 is required.", file=sys.stderr)
        return 2
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8766, metavar="端口", help="本机端口（默认 8766）")
    parser.add_argument("--code-repo", default=os.environ.get("COULI_CODE_REPO"), metavar="目录",
                        help="代码仓库 rebate-platform 的路径（默认取规划仓库的同级目录）")
    parser.add_argument("--runs-dir", default=os.environ.get("COULI_RUNS_DIR"), metavar="目录",
                        help="运行目录 couli-runs 的路径（默认取规划仓库的同级目录）")
    parser.add_argument("--fetch", type=int, default=300, metavar="秒",
                        help=f"每隔多少秒把两个仓库的远端 main 拉到各自的 {FETCH_REF}（默认 300；0 表示不拉取）")
    parser.add_argument("--local", action="store_true",
                        help="规划文档读脚本旁边的本机文件，用来看还没合并的改动（默认读规划仓库的远端 main）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="解析一遍，报告读不到的表、小节或列，不启动服务")
    mode.add_argument("--json", action="store_true", help="把看板数据打印成 JSON")
    mode.add_argument("--export", metavar="文件", help="导出单文件静态快照")
    args = parser.parse_args()

    board = Board(args.code_repo or sibling("rebate-platform"), args.runs_dir or sibling("couli-runs"), args.local)
    if args.check or args.json or args.export:
        if args.fetch:
            board.fetch()
        data = board.get()
        if args.json:
            json.dump(data, sys.stdout, ensure_ascii=False, indent=1)
            print()
        elif args.export:
            Path(args.export).write_text(export_html(data), encoding="utf-8")
            print(f"OK: 已导出 {args.export}")
        else:
            for line in report(data):
                print(line)
        return 1 if args.check and data["warnings"] else 0

    hosts = {f"127.0.0.1:{args.port}", f"localhost:{args.port}"}
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(board, hosts))
    except OSError as error:
        print(f"ERROR: 端口 {args.port} 无法使用（{error}）；换一个端口：--port 8767", file=sys.stderr)
        return 1
    if args.fetch:
        threading.Thread(target=fetch_loop, args=(board, max(args.fetch, 30)), daemon=True).start()
    print(f"凑狸看板：http://127.0.0.1:{args.port}/  （Ctrl+C 停止）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
