# 8-Puzzle A* Solver

An elegant, configuration-driven A* search solver for the classic 8-puzzle sliding tile problem, built using the **[Tiferet](https://github.com/greatstrength/tiferet)** framework.

**ECE 479/579 – Spring 2026 – Homework 3**  
**Due: February 28, 2026**

## Overview

This project implements the A* algorithm to solve any user-provided 8-puzzle configuration (initial state + arbitrary goal state). It supports four admissible heuristics:

- **Misplaced Tiles** (mandatory) — count of tiles not in their goal position
- **Manhattan Distance** (mandatory) — sum of horizontal and vertical distances per tile
- **Manhattan + Linear Conflict** (extension) — adds penalty for tiles blocking each other in rows/columns
- **Additive Pattern Database** (extension) — precomputed exact costs for tile subsets

Key features:
- Accepts flexible puzzle input (comma/space-separated, `*` or `0` for blank).
- Displays the blank tile as `*` by default (configurable via CLI) for better readability.
- Automatically detects **unsolvable** configurations using inversion parity.
- Outputs pretty-printed step-by-step solutions, search metrics (nodes expanded, execution time, path length), and heuristic performance.
- Built-in experiment runner for side-by-side heuristic comparisons.

The solver satisfies all Homework 3 requirements while demonstrating clean, maintainable architecture via Tiferet.

## Background & Motivation

This application was designed specifically for **ECE 479/579 Homework 3 (Spring 2026)**, which requires implementing A* with misplaced tiles and Manhattan distance heuristics, supporting arbitrary start and goal states, handling unsolvability, and comparing efficiency. Optional extensions (additional admissible heuristics) were added to explore more advanced informed search techniques.

Rather than a minimal script, the implementation uses the **Tiferet** framework (https://github.com/greatstrength/tiferet) — a small, elegant Python library that applies Domain-Driven Design (DDD) principles through **domain events** and heavy **YAML configuration**.  

Tiferet lets you define application behavior declaratively:
- Core logic (A* search) lives in one domain event.
- Heuristic selection, CLI args, error messages, input parsing, and output formatting are all driven by YAML files.
- This makes the app highly configurable, extensible (easy to add new heuristics, TUI, JSON output, etc.), and maintainable — turning a homework assignment into a small production-grade example.

The blank tile is shown as `*` (not `0`) in all user-facing output, with internal logic still using `0` for efficiency (hashing, heuristics, solvability checks). This was a deliberate UX choice.

**AI Collaboration Note**  
The core A* implementation, project structure, YAML configurations, heuristic utilities, solvability checker, pretty-printing logic, input parsing, and much of this README were developed in close collaboration with **Grok 4** (built by xAI) and **Oz** (Warp's AI agent, powered by the `auto` model). Grok 4 contributed the initial design blueprint, architectural decisions, and documentation drafting; Oz implemented the full codebase, YAML configurations, and end-to-end verification. All work was iteratively refined through conversation starting February 27, 2026. This transparency aligns with academic integrity and the spirit of exploring AI-assisted development.

## Setup

### Prerequisites

- Python 3.10 or later
- Git

### Installation

```bash
# Clone the repo
git clone https://github.com/greatstrength/ece-579-a-star-8-puzzle.git
cd ece-579-a-star-8-puzzle

# Virtual environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Tiferet + project in editable mode
pip install -e .
```

## Usage

### CLI Examples

```bash
# Default: manhattan heuristic
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5"

# Misplaced tiles
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --heuristic misplaced

# Linear conflict
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --heuristic linear-conflict

# Pattern database
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --heuristic pattern-db

# Custom goal + verbose pretty output
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" \
  --goal "1,2,3,8,*,4,7,6,5" --pretty

# Different blank symbol
python puzzle_cli.py puzzle solve "2 8 3 1 6 4 7 * 5" --blank-symbol "_"
```

See `--help` for full list of supported heuristics and options.

### Input Parsing & 3×3 Grid Correspondence

The solver expects a **flat, row-major** representation of the 3×3 puzzle grid.

- Provide exactly **9 values** (tiles 1–8 + blank).
- Order: left-to-right, top-to-bottom (row-major).
- Accepts commas, spaces, or mixed separators.
- Converts `*` → `0` internally.
- Validates: exactly 9 unique values from 0–8.

#### Visual Mapping Examples

| Input string                          | 3×3 Grid (output display)              |
|---------------------------------------|----------------------------------------|
| `2,8,3,1,6,4,7,*,5`                   | 2 8 3<br>1 6 4<br>7 * 5                |
| `2 8 3 1 6 4 7 * 5`                   | 2 8 3<br>1 6 4<br>7 * 5                |
| `1,2,3,4,5,6,7,8,0`                   | 1 2 3<br>4 5 6<br>7 8 *                |
| `0,1,2,3,4,5,6,7,8`                   | * 1 2<br>3 4 5<br>6 7 8                |
| `1 2 3 4 5 6 7 8 *`                   | 1 2 3<br>4 5 6<br>7 8 *                |

**Why row-major?**  
It matches how humans naturally read and type a grid (row by row), and it’s the same convention used in the pretty-printed output and in the internal `settings.py` utilities (`display_to_internal` and `internal_to_display`).

All domain events work with the internal numeric representation (0 = blank), while CLI and printed results show the display version (`*` by default).

### Heuristic Comparison Runner

```bash
python puzzle_run.py
```

Runs a predefined suite (trivial → hard puzzles + one unsolvable case) with all supported heuristics, printing a side-by-side table of nodes expanded, execution time, and path length.

## Project Structure

```
ece-579-a-star-8-puzzle/
├── puzzle_cli.py              # Loads puzzle_cli interface & runs CLI
├── puzzle_run.py              # Loads puzzle_solver & runs benchmark suite
├── pyproject.toml             # Dependencies (only tiferet + stdlib)
├── README.md
├── docs/
│   └── heuristics-guide.md    # Detailed heuristic explanations, examples & references
└── app/
    ├── events/
    │   ├── puzzle.py          # SolvePuzzle (A*), ValidatePuzzleState, etc.
    │   └── settings.py        # Base utilities: solvability, pretty-print (*), state conversion
    └── configs/
        ├── app.yml            # Interfaces (puzzle_solver, puzzle_cli)
        ├── cli.yml            # Command/arg definitions (--heuristic, --goal, etc.)
        ├── container.yml      # Injects domain events
        ├── error.yml          # Custom errors (unsolvable, invalid state, etc.)
        ├── feature.yml        # puzzle.solve feature + heuristic param
        └── logging.yml        # Optional structured logs
```

## Heuristics

The solver supports four admissible heuristics, selectable via the `--heuristic` CLI flag:

- `misplaced` — Number of tiles not in their goal position (basic, mandatory)
- `manhattan` — Sum of horizontal + vertical distances per tile (basic, mandatory; default)
- `linear-conflict` — Manhattan distance + +2 per row/column conflict (enhanced extension)
- `pattern-db` — Additive pattern database lookup (advanced extension)

All heuristics guarantee optimal paths when used with A*.

For detailed definitions, formulas, examples, properties, comparison rationale, and references, see:

→ [docs/heuristics-guide.md](docs/heuristics-guide.md)

### Quick Heuristics Comparison

| Heuristic                  | Admissible? | Typical Nodes Expanded | Precompute? | Best For                  |
|----------------------------|-------------|------------------------|-------------|---------------------------|
| misplaced                  | Yes         | High                   | No          | Quick baseline            |
| manhattan                  | Yes         | Medium                 | No          | Standard balanced choice  |
| linear-conflict            | Yes         | Low–Medium             | No          | Stronger without overhead |
| pattern-db                 | Yes         | Very Low               | Yes (low)   | Maximum informedness      |

## Unsolvable Cases

Detected via **inversion parity**:
- Flatten state (ignore blank), count inversions (pairs out of order).
- Puzzle is solvable iff start and goal have the same parity (both even or both odd).
- Reported clearly: “This configuration is unsolvable (odd permutation parity).”

## Built With

- **[Tiferet](https://github.com/greatstrength/tiferet)** — Configuration-driven DDD framework (v1.9.x as of Feb 2026)
- Python 3.10+
- Standard library only (no extra ML/math deps)

## License

MIT

## Acknowledgments

- **Grok 4** (xAI) — AI collaborator for initial design blueprint, architecture decisions, and documentation drafting.
- **Oz** (Warp AI agent) — AI collaborator for full code implementation, YAML configurations, end-to-end verification, and benchmark test collection.
- Tiferet maintainers — For an inspiring, beautiful framework.