# 8-Puzzle A* Solver

An A* search solver for the classic 8-puzzle problem, built with the [Tiferet](https://github.com/greatstrength/tiferet) framework.

**ECE 479/579 – Spring 2026 – Homework 3**

## Overview

This application solves the 8-puzzle sliding tile problem using the A* search algorithm with two selectable heuristics:

- **Manhattan Distance** — sum of the horizontal and vertical distances of each tile from its goal position
- **Misplaced Tiles** — count of tiles not in their goal position

The solver accepts any user-provided initial and goal state, detects unsolvable configurations via inversion parity, and reports search efficiency metrics (nodes expanded, execution time, path length).

## Setup

### Prerequisites

- Python 3.10 or later

### Installation

```bash
# Clone the repository
git clone https://github.com/greatstrength/ece-579-a-star-8-puzzle.git
cd ece-579-a-star-8-puzzle

# Create and activate a virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

## Usage

### CLI

Solve a puzzle from the command line:

```bash
# Solve with Manhattan distance (default)
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5"

# Solve with misplaced tiles heuristic
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --heuristic misplaced

# Specify a custom goal state
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --goal "1,2,3,8,*,4,7,6,5"

# Use a different blank symbol
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --blank-symbol "_"
```

### Input Formats

The solver accepts flexible input formats for puzzle states:

- Comma-separated: `1,2,3,4,5,6,7,8,*`
- Space-separated: `1 2 3 4 5 6 7 8 *`
- Use `*` or `0` for the blank tile

### Programmatic Runner

Run the full heuristic comparison suite:

```bash
python puzzle_run.py
```

This executes 8 test cases (trivial through hard, plus an unsolvable case) with both heuristics, producing a side-by-side comparison of nodes expanded, execution time, and path length.

## Project Structure

```
ece-579-a-star-8-puzzle/
├── puzzle_cli.py              # CLI entry point
├── puzzle_run.py              # Programmatic experiment runner
├── pyproject.toml             # Project metadata & dependencies
├── README.md
└── app/
    ├── events/
    │   ├── __init__.py
    │   ├── puzzle.py          # SolvePuzzle — A* search domain event
    │   └── settings.py        # PuzzleEvent — base class with utilities
    └── configs/
        ├── __init__.py
        ├── app.yml            # Interface definitions
        ├── cli.yml            # CLI command definitions
        ├── container.yml      # Dependency injection
        ├── error.yml          # Error messages
        ├── feature.yml        # Feature workflows
        └── logging.yml        # Logging configuration
```

## Heuristics

### Manhattan Distance

For each tile (excluding the blank), calculate the sum of horizontal and vertical distance from its current position to its goal position. This is a more informed heuristic that consistently expands fewer nodes.

### Misplaced Tiles

Count the number of tiles not in their goal position (excluding the blank). A simpler but less informed heuristic.

Both heuristics are **admissible** (never overestimate) and **consistent**, guaranteeing A* finds the optimal solution.

## Unsolvable Detection

The solver automatically detects unsolvable configurations using **inversion parity**. A puzzle state is solvable from a goal state if and only if both states have the same inversion parity (both even or both odd number of inversions, excluding the blank tile).

## Built With

- [Tiferet](https://github.com/greatstrength/tiferet) — Python framework for Domain-Driven Design
- Python 3.10+

## License

MIT
