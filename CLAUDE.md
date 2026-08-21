# LeetCode solutions

A personal LeetCode journal. Each problem lives in `NNNN_problem-slug/` with an `info.md`
(metadata + submission stats) and a `solution.py` / `solution.cpp`.

## Scope

Only edit `generate_readme.py`. The problem directories — `info.md` and the solution files —
are written by hand; do not add, edit, or reformat them. `README.md` and `assets/*.svg` are
generated output, so change them by changing the generator and re-running it, never by hand.

## What generate_readme.py consumes

It walks every directory matching `\d{3,4}_.+` and parses `info.md`, which looks like this:

```markdown
# 114. Flatten Binary Tree to Linked List

| Difficulty | Accepted        |Acceptance Rate |
|:----------:|:---------------:|:--------------:|
|  Medium    | 1,475,505/2.1M  |  71.3%         |

[Question](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/description/)

## Solutions

| Language | Runtime | Runtime Beats | Memory | Memory Beats |     Date   |
|:--------:|:-------:|:-------------:|:------:|:------------:|:----------:|
| Python   |    0 ms | 100.00 %      |19.52 MB| 41.17 %      | 2026-08-20 |
```

Parsing is positional and forgiving about whitespace, but not about order:

- The first `# N. Title` line gives the number and title; without it both fall back to the
  directory name. The first `[Question](url)` link gives the URL, else a URL built from the
  slug.
- **First** table = metadata. Column 0 is the difficulty (must be Easy/Medium/Hard, else the
  directory is skipped), column 2 is the acceptance rate. Column 1 is ignored.
- **Second** table = one row per submission, columns in order: language, runtime, runtime
  beats, memory, memory beats, date. Rows with fewer than 6 cells are dropped.
- Numeric cells are read with a "first number in the cell" regex, so units and `%` are fine.
  Dates must be `YYYY-MM-DD`. A problem's solve date is the earliest date across its rows.
- A directory is skipped (with a warning on stderr) if it has no `info.md`, fewer than two
  tables, an unknown difficulty, or no usable solution row. Those warnings are the main
  signal that a change to the parser broke something.

## Working on the generator

Stdlib only — no dependencies, and keep it that way. The file is laid out in labelled
sections: parsing → aggregation (`Stats`) → SVG helpers (`svg`/`text`/`rect`/`line`/`path`/
`legend`) → the six chart renderers → `render_readme` → `main`. Build new charts out of the
existing helpers rather than emitting raw SVG strings.

Chart constraints, because these render inside GitHub markdown:

- Colors come from the palette constants at the top (`EASY`/`MEDIUM`/`HARD`/`ACCENT`/`MUTED`)
  and must stay readable on both the light and dark GitHub themes — no hardcoded black or
  white, no theme-dependent defaults.
- Charts are drawn at `GRID_W` (440), the width they are displayed at, and every `<svg>` needs
  an intrinsic `width`/`height` as well as a `viewBox` or renderers stretch it.
- Static SVG only: GitHub strips scripts and external references, so no JS, webfonts, or
  remote assets.
- Every renderer must handle the empty case (`empty_chart`) — the axis code divides by counts.
- `CHART_START` (config block at the top) windows the two time-series charts, "Solved over
  time" and "Monthly output", because the early history is too sparse to chart usefully. It
  must not leak into anything else: badges, the at-a-glance table, streaks, recently-solved,
  and the other four charts all stay all-time. `CHART_START = None` means chart everything.

Run it with `python3 generate_readme.py`. Useful flags: `--root`, `--output`, `--assets-dir`,
`--quiet`. It exits 1 if no problem directories parse.
