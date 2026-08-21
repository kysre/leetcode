#!/usr/bin/env python3
"""Regenerate README.md (and its charts) from the per-problem info.md files.

Every solved problem lives in a `NNNN_problem-slug/` directory containing an
`info.md` with the problem metadata and a table of submitted solutions. This
script reads them all and rewrites README.md plus the SVG charts in assets/.

Usage:
    python3 generate_readme.py
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

# The "Solved over time" and "Monthly output" charts start here; the early years
# are sparse enough that charting them all squashes the recent pace into the
# right edge. Set to None to chart the full history. Everything else -- badges,
# the at-a-glance table, the other four charts -- always covers all time.
CHART_START: date | None = date(2026, 6, 1)

# --------------------------------------------------------------------------
# palette -- readable on both the light and the dark GitHub themes
# --------------------------------------------------------------------------

EASY = "#00b8a3"
MEDIUM = "#ffb800"
HARD = "#ff375f"
ACCENT = "#4c8eda"
MUTED = "#8b949e"

DIFFICULTIES = ("Easy", "Medium", "Hard")
DIFF_COLOR = {"Easy": EASY, "Medium": MEDIUM, "Hard": HARD}
FONT = "system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"

# charts sit two-per-row in the README grid, so they are drawn at roughly the
# width they are displayed at -- that keeps the label sizes honest
GRID_W = 440

PROBLEM_DIR_RE = re.compile(r"\d{3,4}_.+")
TITLE_RE = re.compile(r"^#\s+(\d+)\.\s+(.+?)\s*$")
LINK_RE = re.compile(r"\[Question\]\(\s*(\S+?)\s*\)")
SEPARATOR_CELL_RE = re.compile(r"^:?-{2,}:?$")


# --------------------------------------------------------------------------
# data model
# --------------------------------------------------------------------------


@dataclass
class Solution:
    language: str
    runtime_ms: float | None
    runtime_beats: float | None
    memory_mb: float | None
    memory_beats: float | None
    solved_on: date | None


@dataclass
class Problem:
    number: int
    title: str
    slug: str
    difficulty: str
    acceptance_rate: float | None
    url: str
    solutions: list[Solution] = field(default_factory=list)

    @property
    def solved_on(self) -> date | None:
        dates = [s.solved_on for s in self.solutions if s.solved_on]
        return min(dates) if dates else None


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


def parse_number(cell: str) -> float | None:
    """Pull a float out of cells like `31 ms`, `98.75 %`, `23.56 MB`, `72.5%`."""
    match = re.search(r"-?\d+(?:\.\d+)?", cell.replace(",", ""))
    return float(match.group()) if match else None


def parse_date(cell: str) -> date | None:
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", cell)
    if not match:
        return None
    try:
        return date(int(match[1]), int(match[2]), int(match[3]))
    except ValueError:
        return None


def parse_tables(text: str) -> list[list[list[str]]]:
    """Split markdown text into tables, each a list of rows of stripped cells."""
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not all(SEPARATOR_CELL_RE.match(c) for c in cells if c):
                current.append(cells)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def parse_info_md(directory: Path) -> tuple[Problem | None, str | None]:
    """Parse one problem directory. Returns (problem, warning)."""
    info_path = directory / "info.md"
    if not info_path.is_file():
        return None, "no info.md"

    text = info_path.read_text(encoding="utf-8")

    title_match = None
    for line in text.splitlines():
        title_match = TITLE_RE.match(line)
        if title_match:
            break

    slug_number, _, slug_rest = directory.name.partition("_")
    if title_match:
        number, title = int(title_match[1]), title_match[2]
    else:
        number, title = int(slug_number), slug_rest.replace("-", " ").title()

    link_match = LINK_RE.search(text)
    url = link_match[1] if link_match else f"https://leetcode.com/problems/{slug_rest}/"

    tables = parse_tables(text)
    if len(tables) < 2:
        return None, "expected a metadata table and a solutions table"

    meta_rows = tables[0][1:]
    if not meta_rows:
        return None, "metadata table has no data row"
    meta = meta_rows[0]
    difficulty = meta[0].title() if meta and meta[0] else "Unknown"
    if difficulty not in DIFF_COLOR:
        return None, f"unknown difficulty {meta[0]!r}"
    acceptance_rate = parse_number(meta[2]) if len(meta) > 2 else None

    solutions: list[Solution] = []
    for row in tables[1][1:]:
        if len(row) < 6 or not row[0]:
            continue
        solutions.append(
            Solution(
                language=row[0],
                runtime_ms=parse_number(row[1]),
                runtime_beats=parse_number(row[2]),
                memory_mb=parse_number(row[3]),
                memory_beats=parse_number(row[4]),
                solved_on=parse_date(row[5]),
            )
        )
    if not solutions:
        return None, "solutions table has no data row"

    problem = Problem(
        number, title, directory.name, difficulty, acceptance_rate, url, solutions
    )
    warning = None if problem.solved_on else "no valid solution date"
    return problem, warning


def collect_problems(root: Path) -> tuple[list[Problem], list[str]]:
    problems: list[Problem] = []
    warnings: list[str] = []
    for directory in sorted(p for p in root.iterdir() if p.is_dir()):
        if not PROBLEM_DIR_RE.fullmatch(directory.name):
            continue
        problem, warning = parse_info_md(directory)
        if warning:
            warnings.append(f"{directory.name}: {warning}")
        if problem:
            problems.append(problem)
    problems.sort(key=lambda p: p.number)
    return problems, warnings


# --------------------------------------------------------------------------
# aggregation
# --------------------------------------------------------------------------


@dataclass
class Stats:
    problems: list[Problem]
    solutions: list[Solution]
    by_difficulty: Counter
    by_language: Counter
    solve_dates: list[date]
    cumulative: list[tuple[date, int]]
    monthly: list[tuple[date, dict[str, int]]]
    first_solve: date | None
    last_solve: date | None
    longest_streak: int
    current_streak: int
    best_day: tuple[date, int] | None
    avg_runtime_beats: float | None
    avg_memory_beats: float | None


def month_floor(day: date) -> date:
    return day.replace(day=1)


def next_month(day: date) -> date:
    return date(day.year + (day.month == 12), day.month % 12 + 1, 1)


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compute_stats(problems: list[Problem], today: date) -> Stats:
    solutions = [s for p in problems for s in p.solutions]
    dated = [(p.solved_on, p) for p in problems if p.solved_on]
    dated.sort(key=lambda item: item[0])

    cumulative = [(day, i + 1) for i, (day, _) in enumerate(dated)]
    solve_dates = [day for day, _ in dated]

    monthly: list[tuple[date, dict[str, int]]] = []
    if dated:
        buckets: dict[date, dict[str, int]] = defaultdict(
            lambda: dict.fromkeys(DIFFICULTIES, 0)
        )
        for day, problem in dated:
            buckets[month_floor(day)][problem.difficulty] += 1
        cursor, end = month_floor(dated[0][0]), month_floor(dated[-1][0])
        while cursor <= end:
            monthly.append((cursor, buckets[cursor]))
            cursor = next_month(cursor)

    distinct = sorted(set(solve_dates))
    longest = streak = 0
    for i, day in enumerate(distinct):
        streak = streak + 1 if i and day - distinct[i - 1] == timedelta(days=1) else 1
        longest = max(longest, streak)

    current = 0
    if distinct and today - distinct[-1] <= timedelta(days=1):
        current, cursor = 1, distinct[-1]
        for day in reversed(distinct[:-1]):
            if cursor - day != timedelta(days=1):
                break
            current, cursor = current + 1, day

    day_counts = Counter(solve_dates)
    best_day = (
        max(day_counts.items(), key=lambda kv: (kv[1], kv[0])) if day_counts else None
    )

    return Stats(
        problems=problems,
        solutions=solutions,
        by_difficulty=Counter(p.difficulty for p in problems),
        by_language=Counter(s.language for s in solutions),
        solve_dates=solve_dates,
        cumulative=cumulative,
        monthly=monthly,
        first_solve=distinct[0] if distinct else None,
        last_solve=distinct[-1] if distinct else None,
        longest_streak=longest,
        current_streak=current,
        best_day=best_day,
        avg_runtime_beats=mean(
            [s.runtime_beats for s in solutions if s.runtime_beats is not None]
        ),
        avg_memory_beats=mean(
            [s.memory_beats for s in solutions if s.memory_beats is not None]
        ),
    )


# --------------------------------------------------------------------------
# svg helpers
# --------------------------------------------------------------------------


def num(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def svg(width: int, height: int, body: str) -> str:
    # an intrinsic pixel size matters: an SVG sized only in percent has no
    # intrinsic dimensions, so renderers that ignore the grid's column widths
    # stretch it to fill the page instead of drawing it at panel size
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" font-family="{FONT}">\n{body}\n</svg>\n'
    )


def text(
    x: float,
    y: float,
    content: str,
    size: float = 12,
    fill: str = MUTED,
    anchor: str = "start",
    weight: str = "normal",
    opacity: float = 1.0,
) -> str:
    return (
        f'<text x="{num(x)}" y="{num(y)}" font-size="{num(size)}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" opacity="{num(opacity)}">'
        f"{escape(str(content))}</text>"
    )


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    radius: float = 0,
    opacity: float = 1.0,
) -> str:
    return (
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(max(w, 0))}" height="{num(max(h, 0))}" '
        f'rx="{num(radius)}" fill="{fill}" opacity="{num(opacity)}"/>'
    )


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    stroke: str = MUTED,
    width: float = 1,
    opacity: float = 1.0,
    dash: str = "",
) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{num(x1)}" y1="{num(y1)}" x2="{num(x2)}" y2="{num(y2)}" stroke="{stroke}" '
        f'stroke-width="{num(width)}" opacity="{num(opacity)}"{dash_attr}/>'
    )


def circle(cx: float, cy: float, r: float, fill: str, opacity: float = 1.0) -> str:
    return (
        f'<circle cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}" fill="{fill}" '
        f'opacity="{num(opacity)}"/>'
    )


def path(
    d: str,
    fill: str = "none",
    stroke: str = "none",
    width: float = 1,
    opacity: float = 1.0,
) -> str:
    return (
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{num(width)}" '
        f'stroke-linejoin="round" stroke-linecap="round" opacity="{num(opacity)}"/>'
    )


def legend(x: float, y: float, entries: list[tuple[str, str]], size: float = 9) -> str:
    parts, cursor = [], x
    swatch = size * 0.85
    for label, color in entries:
        parts.append(rect(cursor, y - swatch * 0.85, swatch, swatch, color, radius=1.5))
        parts.append(text(cursor + swatch + 4, y, label, size=size))
        cursor += swatch + 16 + len(label) * size * 0.62
    return "\n".join(parts)


def nice_step(span: float, target_ticks: int = 5) -> float:
    """Round a raw axis step up to the nearest 1/2/5 x 10^n."""
    if span <= 0:
        return 1
    raw = span / max(target_ticks, 1)
    magnitude = 10 ** math.floor(math.log10(raw))
    for factor in (1, 2, 5, 10):
        if raw <= factor * magnitude:
            return factor * magnitude
    return 10 * magnitude


def month_ticks(start: date, end: date, max_labels: int) -> list[date]:
    """Month boundaries within [start, end], thinned to at most max_labels."""
    cursor = start if start.day == 1 else next_month(start)
    months = []
    while cursor <= end:
        months.append(cursor)
        cursor = next_month(cursor)
    if len(months) < 2:
        return months
    for step in (1, 2, 3, 6, 12, 24, 60):
        if math.ceil(len(months) / step) <= max_labels:
            break
    return months[::step]


def tick_labels(days: list[date]) -> list[str]:
    """Name the year on the first tick, then only when it changes."""
    labels, previous = [], None
    for day in days:
        labels.append(day.strftime("%b" if day.year == previous else "%b %Y"))
        previous = day.year
    return labels


def empty_chart(width: int, height: int, message: str = "no data yet") -> str:
    return svg(
        width, height, text(width / 2, height / 2, message, size=11, anchor="middle")
    )


# --------------------------------------------------------------------------
# charts
# --------------------------------------------------------------------------


def render_cumulative(stats: Stats, today: date) -> str:
    width, height = GRID_W, 260
    left, right, top, bottom = 30, 12, 20, 28
    if CHART_START:
        # running totals are kept, so the line picks up where the window opens
        baseline = max((v for d, v in stats.cumulative if d < CHART_START), default=0)
        series = [(d, v) for d, v in stats.cumulative if d >= CHART_START]
    else:
        baseline, series = 0, stats.cumulative
    if not series:
        return empty_chart(width, height)

    plot_w, plot_h = width - left - right, height - top - bottom
    start = CHART_START or series[0][0]
    end = max(series[-1][0], today)
    span_days = max((end - start).days, 1)
    total = series[-1][1]
    step = nice_step(total, 4)
    y_max = max(math.ceil(total / step) * step, step)

    def px(day: date) -> float:
        return left + (day - start).days / span_days * plot_w

    def py(value: float) -> float:
        return top + plot_h - value / y_max * plot_h

    parts = []
    tick = 0.0
    while tick <= y_max + 1e-9:
        y = py(tick)
        parts.append(line(left, y, width - right, y, MUTED, 1, 0.2))
        parts.append(text(left - 6, y + 3, int(tick), size=9, anchor="end"))
        tick += step

    # step line: hold the previous total until the next solve lands
    points: list[tuple[float, float]] = [(px(start), py(baseline))]
    for day, value in series:
        points.append((px(day), py(value - 1)))
        points.append((px(day), py(value)))
    points.append((px(end), py(total)))

    trace = " ".join(
        f"{'M' if i == 0 else 'L'}{num(x)} {num(y)}" for i, (x, y) in enumerate(points)
    )
    area = f"{trace} L{num(px(end))} {num(py(0))} L{num(px(start))} {num(py(0))} Z"
    parts.append(path(area, fill=ACCENT, opacity=0.16))
    parts.append(path(trace, stroke=ACCENT, width=1.8))
    parts.append(circle(px(series[-1][0]), py(total), 3.2, ACCENT))
    parts.append(
        text(
            px(end) - 2,
            py(total) - 9,
            f"{total} solved",
            size=10,
            fill=ACCENT,
            anchor="end",
            weight="600",
        )
    )
    if baseline:
        parts.append(
            text(px(start) + 4, py(baseline) - 6, f"{baseline} before", size=9)
        )

    parts.append(line(left, py(0), width - right, py(0), MUTED, 1, 0.55))
    # budget on the long "Mmm YYYY" form -- the first label always carries a year
    max_labels = max(2, int(plot_w // 58))
    ticks = month_ticks(start, end, max_labels)
    if len(ticks) < 2:
        # window shorter than two month boundaries: fall back to day-level ticks
        count = min(max_labels, max(2, span_days // 7 + 1))
        ticks = [
            start + timedelta(days=round(span_days * i / (count - 1)))
            for i in range(count)
        ]
        labels = [day.strftime("%b %d") for day in ticks]
    else:
        labels = tick_labels(ticks)

    for day, label in zip(ticks, labels):
        x = px(day)
        near_left, near_right = x - left < 12, width - right - x < 12
        anchor = "start" if near_left else "end" if near_right else "middle"
        parts.append(text(x, height - 10, label, size=9, anchor=anchor))

    return svg(width, height, "\n".join(parts))


def render_monthly(stats: Stats) -> str:
    width, height = GRID_W, 260
    left, right, top, bottom = 28, 12, 28, 28
    months = stats.monthly
    if CHART_START:
        # bars are whole months, so a mid-month cutoff rounds out to its month
        months = [(m, c) for m, c in months if m >= month_floor(CHART_START)]
    if not months:
        return empty_chart(width, height)

    plot_w, plot_h = width - left - right, height - top - bottom
    totals = [sum(counts.values()) for _, counts in months]
    step = nice_step(max(totals), 4)
    y_max = max(math.ceil(max(totals) / step) * step, step)
    slot = plot_w / len(months)
    bar_w = min(slot * 0.72, 20)

    parts = []
    tick = 0.0
    while tick <= y_max + 1e-9:
        y = top + plot_h - tick / y_max * plot_h
        parts.append(line(left, y, width - right, y, MUTED, 1, 0.2))
        parts.append(text(left - 6, y + 3, int(tick), size=9, anchor="end"))
        tick += step

    last = len(months) - 1
    label_every = math.ceil(len(months) / 6)
    labelled = set(range(0, len(months), label_every))
    # always name the final month, but not on top of the previous label
    if last - max(labelled) >= label_every * 0.6:
        labelled.add(last)
    else:
        labelled.discard(max(labelled))
        labelled.add(last)

    for i, (month, counts) in enumerate(months):
        x = left + slot * i + (slot - bar_w) / 2
        y = top + plot_h
        for difficulty in DIFFICULTIES:
            count = counts.get(difficulty, 0)
            if not count:
                continue
            bar_h = count / y_max * plot_h
            y -= bar_h
            parts.append(rect(x, y, bar_w, bar_h, DIFF_COLOR[difficulty], radius=1.5))
        if i in labelled:
            parts.append(
                text(
                    x + bar_w / 2,
                    height - 10,
                    month.strftime("%b %y"),
                    size=9,
                    anchor="middle",
                )
            )

    parts.append(line(left, top + plot_h, width - right, top + plot_h, MUTED, 1, 0.55))
    parts.append(legend(left, 14, [(d, DIFF_COLOR[d]) for d in DIFFICULTIES]))
    return svg(width, height, "\n".join(parts))


def render_difficulty(stats: Stats) -> str:
    width, height = GRID_W, 240
    total = sum(stats.by_difficulty.values())
    if not total:
        return empty_chart(width, height)

    cx, cy, outer, inner = 112, 122, 74, 47
    parts = []
    angle = -math.pi / 2
    for difficulty in DIFFICULTIES:
        count = stats.by_difficulty.get(difficulty, 0)
        if not count:
            continue
        sweep = 2 * math.pi * count / total
        end = angle + sweep
        large = 1 if sweep > math.pi else 0
        if count == total:  # a single full ring needs two arcs to draw
            parts.append(
                path(
                    f"M{cx} {cy - outer} A{outer} {outer} 0 1 1 {cx - 0.01} {cy - outer} Z "
                    f"M{cx} {cy - inner} A{inner} {inner} 0 1 0 {cx - 0.01} {cy - inner} Z",
                    fill=DIFF_COLOR[difficulty],
                )
            )
        else:
            x1, y1 = cx + outer * math.cos(angle), cy + outer * math.sin(angle)
            x2, y2 = cx + outer * math.cos(end), cy + outer * math.sin(end)
            x3, y3 = cx + inner * math.cos(end), cy + inner * math.sin(end)
            x4, y4 = cx + inner * math.cos(angle), cy + inner * math.sin(angle)
            parts.append(
                path(
                    f"M{num(x1)} {num(y1)} A{outer} {outer} 0 {large} 1 {num(x2)} {num(y2)} "
                    f"L{num(x3)} {num(y3)} A{inner} {inner} 0 {large} 0 {num(x4)} {num(y4)} Z",
                    fill=DIFF_COLOR[difficulty],
                )
            )
        angle = end

    parts.append(
        text(cx, cy + 2, total, size=26, fill=ACCENT, anchor="middle", weight="700")
    )
    parts.append(text(cx, cy + 19, "solved", size=10, anchor="middle"))

    swatch_x, bar_x = 210, 226
    bar_w = width - 14 - bar_x
    y = 74
    for difficulty in DIFFICULTIES:
        count = stats.by_difficulty.get(difficulty, 0)
        share = count / total * 100
        parts.append(rect(swatch_x, y - 9, 10, 10, DIFF_COLOR[difficulty], radius=2.5))
        parts.append(
            text(
                bar_x, y, difficulty, size=12, fill=DIFF_COLOR[difficulty], weight="600"
            )
        )
        parts.append(
            text(width - 14, y, f"{count} · {share:.0f}%", size=11, anchor="end")
        )
        parts.append(rect(bar_x, y + 7, bar_w, 5, MUTED, radius=2.5, opacity=0.22))
        parts.append(
            rect(
                bar_x,
                y + 7,
                bar_w * count / total,
                5,
                DIFF_COLOR[difficulty],
                radius=2.5,
            )
        )
        y += 46

    return svg(width, height, "\n".join(parts))


def render_beats(stats: Stats) -> str:
    width, height = GRID_W, 300
    left, right, top, bottom = 36, 14, 26, 36
    points = [
        (s.runtime_beats, s.memory_beats, p.difficulty)
        for p in stats.problems
        for s in p.solutions
        if s.runtime_beats is not None and s.memory_beats is not None
    ]
    if not points:
        return empty_chart(width, height)

    plot_w, plot_h = width - left - right, height - top - bottom
    parts = []
    for value in range(0, 101, 25):
        x = left + value / 100 * plot_w
        y = top + plot_h - value / 100 * plot_h
        parts.append(line(x, top, x, top + plot_h, MUTED, 1, 0.16))
        parts.append(line(left, y, left + plot_w, y, MUTED, 1, 0.16))
        parts.append(text(x, height - 24, value, size=9, anchor="middle"))
        parts.append(text(left - 6, y + 3, value, size=9, anchor="end"))

    mid_x, mid_y = left + plot_w / 2, top + plot_h / 2
    parts.append(line(mid_x, top, mid_x, top + plot_h, MUTED, 1, 0.4, dash="4 4"))
    parts.append(line(left, mid_y, left + plot_w, mid_y, MUTED, 1, 0.4, dash="4 4"))
    parts.append(
        text(mid_x + 6, mid_y - 6, "fast + lean →", size=9, fill=ACCENT, opacity=0.8)
    )

    for runtime_beats, memory_beats, difficulty in points:
        x = left + runtime_beats / 100 * plot_w
        y = top + plot_h - memory_beats / 100 * plot_h
        parts.append(circle(x, y, 4.5, DIFF_COLOR[difficulty], opacity=0.7))

    parts.append(
        text(left + plot_w / 2, height - 8, "runtime beats %", size=9, anchor="middle")
    )
    parts.append(
        f'<g transform="translate(10 {num(top + plot_h / 2)}) rotate(-90)">'
        f"{text(0, 0, 'memory beats %', size=9, anchor='middle')}</g>"
    )
    parts.append(legend(left, 13, [(d, DIFF_COLOR[d]) for d in DIFFICULTIES]))
    return svg(width, height, "\n".join(parts))


def render_heatmap(stats: Stats, today: date) -> str:
    weeks = 53
    width, left, right, top = GRID_W, 8, 8, 18
    slot = (width - left - right) / weeks
    cell = slot * 0.8
    height = round(top + 7 * slot + 30)
    if not stats.solve_dates:
        return empty_chart(width, height)

    counts = Counter(stats.solve_dates)
    # columns run Sunday-to-Saturday, ending with the week containing today
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    start = last_sunday - timedelta(weeks=weeks - 1)
    ramp = [0.16, 0.4, 0.62, 0.82, 1.0]

    parts = []
    seen_months = set()
    for week in range(weeks):
        for weekday in range(7):
            day = start + timedelta(weeks=week, days=weekday)
            if day > today:
                continue
            x = left + week * slot
            y = top + weekday * slot
            count = counts.get(day, 0)
            color = ACCENT if count else MUTED
            opacity = ramp[min(count, len(ramp) - 1)] if count else 0.14
            parts.append(rect(x, y, cell, cell, color, radius=1.5, opacity=opacity))
            if day.day <= 7 and day.month not in seen_months:
                seen_months.add(day.month)
                parts.append(text(x, top - 6, day.strftime("%b"), size=8))

    total = sum(
        counts.get(start + timedelta(days=i), 0)
        for i in range((today - start).days + 1)
    )
    parts.append(text(left, height - 8, f"{total} in the last year", size=9))
    legend_x = width - right - 5 * slot - 30
    parts.append(text(legend_x - 5, height - 8, "less", size=8, anchor="end"))
    for i, opacity in enumerate([0.14] + ramp[1:]):
        color = MUTED if i == 0 else ACCENT
        parts.append(
            rect(
                legend_x + i * slot,
                height - 16,
                cell,
                cell,
                color,
                radius=1.5,
                opacity=opacity,
            )
        )
    parts.append(text(legend_x + 4 * slot + cell + 5, height - 8, "more", size=8))
    return svg(width, height, "\n".join(parts))


def render_languages(stats: Stats) -> str:
    entries = stats.by_language.most_common()
    width = GRID_W
    row_h, top = 30, 16
    height = top + row_h * max(len(entries), 1) + 6
    if not entries:
        return empty_chart(width, 110)

    label_w, right = 62, 58
    bar_w = width - label_w - right
    total = sum(count for _, count in entries)
    biggest = entries[0][1]

    parts = []
    for i, (language, count) in enumerate(entries):
        y = top + i * row_h
        parts.append(
            text(label_w - 8, y + 12, language, size=11, anchor="end", weight="600")
        )
        parts.append(rect(label_w, y + 2, bar_w, 13, MUTED, radius=6.5, opacity=0.16))
        parts.append(
            rect(label_w, y + 2, bar_w * count / biggest, 13, ACCENT, radius=6.5)
        )
        parts.append(
            text(
                width - 10,
                y + 12,
                f"{count} ({count / total * 100:.0f}%)",
                size=10,
                anchor="end",
            )
        )
    return svg(width, height, "\n".join(parts))


# --------------------------------------------------------------------------
# readme
# --------------------------------------------------------------------------


def bar(value: int, total: int, slots: int = 20) -> str:
    filled = round(value / total * slots) if total else 0
    return "█" * filled + "░" * (slots - filled)


def badge(label: str, message: str, color: str) -> str:
    def quote(part: str) -> str:
        return part.replace("-", "--").replace("_", "__").replace(" ", "_")

    url = f"https://img.shields.io/badge/{quote(label)}-{quote(message)}-{color.lstrip('#')}"
    return f"![{label}: {message}]({url})"


def render_readme(stats: Stats, assets: str, today: date) -> str:
    total = len(stats.problems)
    lines: list[str] = []
    add = lines.append

    add("# 🧩 LeetCode Journey")
    add("")
    add("My solved LeetCode problems, one directory per question.")
    add(
        "This page is generated from every `info.md` by [`generate_readme.py`](generate_readme.py)."
    )
    add("")
    add(
        " ".join(
            [
                badge("Solved", str(total), ACCENT),
                badge("Easy", str(stats.by_difficulty.get("Easy", 0)), EASY),
                badge("Medium", str(stats.by_difficulty.get("Medium", 0)), MEDIUM),
                badge("Hard", str(stats.by_difficulty.get("Hard", 0)), HARD),
            ]
        )
    )
    add("")
    add("## 📊 At a glance")
    add("")
    add("| | |")
    add("|:--|:--|")
    add(f"| **Problems solved** | {total} |")
    add(f"| **Submissions recorded** | {len(stats.solutions)} |")
    for difficulty in DIFFICULTIES:
        count = stats.by_difficulty.get(difficulty, 0)
        share = count / total * 100 if total else 0
        add(f"| **{difficulty}** | `{bar(count, total)}` {count} ({share:.0f}%) |")
    languages = ", ".join(
        f"{lang} ({count})" for lang, count in stats.by_language.most_common()
    )
    add(f"| **Languages** | {languages or '—'} |")
    if stats.avg_runtime_beats is not None:
        add(f"| **Avg. runtime beats** | {stats.avg_runtime_beats:.1f}% |")
    if stats.avg_memory_beats is not None:
        add(f"| **Avg. memory beats** | {stats.avg_memory_beats:.1f}% |")
    if stats.first_solve:
        add(f"| **First solve** | {stats.first_solve:%b %d, %Y} |")
    if stats.last_solve:
        days_ago = (today - stats.last_solve).days
        suffix = (
            "today"
            if days_ago == 0
            else "yesterday" if days_ago == 1 else f"{days_ago} days ago"
        )
        add(f"| **Latest solve** | {stats.last_solve:%b %d, %Y} ({suffix}) |")
    add(f"| **Longest streak** | {stats.longest_streak} day(s) |")
    add(f"| **Current streak** | {stats.current_streak} day(s) |")
    if stats.best_day:
        day, count = stats.best_day
        add(f"| **Busiest day** | {day:%b %d, %Y} — {count} problem(s) |")
    add("")

    window = f" (since {CHART_START:%b %Y})" if CHART_START else ""
    grid = [
        [
            (
                f"📈 Solved over time{window}",
                "cumulative.svg",
                "Cumulative problems solved",
            ),
            (
                f"🗓️ Monthly output{window}",
                "monthly.svg",
                "Problems per month by difficulty",
            ),
        ],
        [
            ("🎯 Difficulty mix", "difficulty.svg", "Difficulty breakdown"),
            ("⚡ Solution quality", "beats.svg", "Runtime beats vs memory beats"),
        ],
        [
            ("🔥 Activity", "heatmap.svg", "Solve activity over the last year"),
            ("💻 Languages", "languages.svg", "Solutions per language"),
        ],
    ]
    add("## 📉 The journey in six charts")
    add("")
    add("<table>")
    for row in grid:
        add("<tr>")
        for heading, filename, alt in row:
            add('<td width="50%" valign="top">')
            add(f"<b>{heading}</b><br>")
            add(f'<img src="{assets}/{filename}" alt="{alt}" width="{GRID_W}"><br>')
            add("</td>")
        add("</tr>")
    add("</table>")
    add("")

    recent = sorted(
        ((s, p) for p in stats.problems for s in p.solutions if s.solved_on),
        key=lambda item: (item[0].solved_on, item[1].number),
        reverse=True,
    )[:10]
    if recent:
        add("## 🕒 Recently solved")
        add("")
        add(
            "| Date | # | Problem | Difficulty | Language | Runtime beats | Memory beats |"
        )
        add("|:--|--:|:--|:--|:--|--:|--:|")
        for solution, problem in recent:
            runtime = (
                f"{solution.runtime_beats:.2f}%"
                if solution.runtime_beats is not None
                else "—"
            )
            memory = (
                f"{solution.memory_beats:.2f}%"
                if solution.memory_beats is not None
                else "—"
            )
            add(
                f"| {solution.solved_on:%Y-%m-%d} | {problem.number} "
                f"| [{problem.title}]({problem.url}) | {problem.difficulty} "
                f"| {solution.language} | {runtime} | {memory} |"
            )
        add("")

    add("---")
    add("")
    add(f"<sub>Generated by <code>generate_readme.py</code> on {today:%Y-%m-%d}.</sub>")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    default_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=default_root, help="repository root"
    )
    parser.add_argument(
        "--output", default="README.md", help="README path, relative to root"
    )
    parser.add_argument(
        "--assets-dir", default="assets", help="chart directory, relative to root"
    )
    parser.add_argument("--quiet", action="store_true", help="only print warnings")
    args = parser.parse_args(argv)

    root: Path = args.root.resolve()
    problems, warnings = collect_problems(root)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if not problems:
        print(f"error: no problem directories found under {root}", file=sys.stderr)
        return 1

    today = date.today()
    stats = compute_stats(problems, today)

    assets_dir = root / args.assets_dir
    assets_dir.mkdir(parents=True, exist_ok=True)
    charts = {
        "cumulative.svg": render_cumulative(stats, today),
        "monthly.svg": render_monthly(stats),
        "difficulty.svg": render_difficulty(stats),
        "beats.svg": render_beats(stats),
        "heatmap.svg": render_heatmap(stats, today),
        "languages.svg": render_languages(stats),
    }
    for filename, content in charts.items():
        (assets_dir / filename).write_text(content, encoding="utf-8")

    readme_path = root / args.output
    readme_path.write_text(
        render_readme(stats, args.assets_dir, today), encoding="utf-8"
    )

    if not args.quiet:
        print(
            f"{len(problems)} problems, {len(stats.solutions)} submissions "
            f"-> {readme_path.name} + {len(charts)} charts in {args.assets_dir}/"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
