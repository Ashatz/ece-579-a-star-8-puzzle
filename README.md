# 8-Puzzle A* Solver

An elegant, configuration-driven A* search solver for the classic 8-puzzle sliding tile problem, built using the **[Tiferet](https://github.com/greatstrength/tiferet)** framework.

**ECE 479/579 – Spring 2026 – Homework 3**  
**Due: February 28, 2026**

## Overview

This project implements the A* algorithm to solve any user-provided 8-puzzle configuration (initial state + arbitrary goal state). It compares two mandatory admissible heuristics:

- **Manhattan Distance** — the sum of horizontal and vertical distances each tile must travel to reach its goal position (excluding the blank). A stronger, more informed heuristic that typically expands far fewer nodes.
- **Misplaced Tiles** (tiles-out-of-place) — simply counts how many tiles are not in their correct goal position (excluding the blank). Simpler and faster to compute, but less informative, leading to more nodes explored.

Key features:
- Accepts flexible puzzle input (comma/space-separated, `*` or `0` for blank).
- Displays the blank tile as `*` by default (configurable via CLI) for better readability.
- Automatically detects **unsolvable** configurations using inversion parity.
- Outputs pretty-printed step-by-step solutions, search metrics (nodes expanded, execution time, path length), and heuristic performance.
- Built-in experiment runner for side-by-side heuristic comparisons.

The solver satisfies all Homework 3 requirements while demonstrating clean, maintainable architecture via Tiferet.

## Background & Motivation

This application was designed specifically for **ECE 479/579 Homework 3 (Spring 2026)**, which asks students to explore heuristic power in A* for the 8-puzzle using Manhattan distance and misplaced tiles, allow arbitrary start/goal states, handle unsolvability, and compare efficiency.

Rather than a minimal script, the implementation uses the **Tiferet** framework (https://github.com/greatstrength/tiferet) — a small, elegant Python library that applies Domain-Driven Design (DDD) principles through **domain events** and heavy **YAML configuration**.  

Tiferet (inspired by the Kabbalistic concept of balance and beauty) lets you define application behavior declaratively:
- Core logic (A* search) lives in one domain event.
- Heuristic selection, CLI args, error messages, input parsing, and output formatting are all driven by YAML files.
- This makes the app highly configurable, extensible (easy to add a third heuristic, TUI, JSON output, etc.), and maintainable — turning a homework assignment into a small production-grade example.

The blank tile is shown as `*` (not `0`) in all user-facing output, with internal logic still using `0` for efficiency (hashing, heuristics, solvability checks). This was a deliberate UX choice discussed during design.

**AI Collaboration Note**  
The core A* implementation, project structure, YAML configurations, heuristic utilities, solvability checker, pretty-printing logic, input parsing, and much of this README were developed in close collaboration with **Grok 4** (built by xAI) and **Oz** (Warp's AI agent, powered by the `auto` model). Grok 4 contributed the initial design blueprint and architectural decisions; Oz implemented the full codebase, YAML configurations, and end-to-end verification. All work was iteratively refined through conversation starting February 27, 2026. This transparency aligns with academic integrity and the spirit of exploring AI-assisted development.

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
# Default: Manhattan distance, blank = *
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5"

# Misplaced tiles heuristic
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --heuristic misplaced

# Custom goal + verbose pretty output
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" \
  --goal "1,2,3,8,*,4,7,6,5" --pretty

# Different blank symbol
python puzzle_cli.py puzzle solve "2 8 3 1 6 4 7 * 5" --blank-symbol "_"
```

### Input Parsing & 3×3 Grid Correspondence

The solver expects a **flat, row-major** representation of the 3×3 puzzle grid. This is the standard way to convert a 2D puzzle into a single line of input.

#### How it works:
1. You provide exactly **9 values** (the tiles 1–8 plus the blank).
2. The order is **left-to-right, top-to-bottom** (row-major order).
3. The parser automatically:
   - Accepts commas, spaces, or mixed separators
   - Converts `*` → `0` (internal blank)
   - Converts the flat list into a 3×3 tuple-of-tuples for internal use
   - Validates: exactly 9 unique numbers from 0–8

#### Visual Mapping Examples

| Input string                          | 3×3 Grid (what you see in output)      |
|---------------------------------------|----------------------------------------|
| `2,8,3,1,6,4,7,*,5`                   | 2 8 3<br>1 6 4<br>7 * 5                |
| `2 8 3 1 6 4 7 * 5`                   | 2 8 3<br>1 6 4<br>7 * 5                |
| `1,2,3,4,5,6,7,8,0`                   | 1 2 3<br>4 5 6<br>7 8 *                |
| `0,1,2,3,4,5,6,7,8`                   | * 1 2<br>3 4 5<br>6 7 8                |
| `1 2 3 4 5 6 7 8 *`                   | 1 2 3<br>4 5 6<br>7 8 *                |

**Why row-major?**  
It matches how humans naturally read and type a grid (row by row), and it’s the same convention used in the pretty-printed output and in the internal `settings.py` utilities (`display_to_internal` and `internal_to_display`).

All domain events (SolvePuzzle, ValidatePuzzleState, etc.) work with the **internal numeric representation** (0 = blank), while the CLI and printed results always show the **display version** (`*` by default). This separation keeps the A* algorithm clean and fast while giving you a beautiful user experience.

### Heuristic Comparison Runner

```bash
python puzzle_run.py
```

Runs a predefined suite (trivial → hard puzzles + one unsolvable case) with both heuristics, printing a side-by-side table of nodes expanded, execution time, and path length.

## Project Structure

```
ece-579-a-star-8-puzzle/
├── puzzle_cli.py              # Loads puzzle_cli interface & runs CLI
├── puzzle_run.py              # Loads puzzle_solver & runs benchmark suite
├── pyproject.toml             # Dependencies (only tiferet + stdlib)
├── README.md
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

## Heuristics in Depth

| Heuristic          | Admissible? | Consistency? | Typical Nodes Expanded | Computation Cost | Informativeness |
|--------------------|-------------|--------------|------------------------|------------------|-----------------|
| Manhattan Distance | Yes         | Yes          | Low–Medium             | Medium           | High            |
| Misplaced Tiles    | Yes         | Yes          | High                   | Very Low         | Low             |

Both guarantee optimal paths. Manhattan usually wins on efficiency (fewer expansions) because it better approximates true cost-to-goal.

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
- **Oz** (Warp AI agent) — AI collaborator for full code implementation, YAML configurations, end-to-end verification, and README finalization.
- Tiferet maintainers — For an inspiring, beautiful framework.
