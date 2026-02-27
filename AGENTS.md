# AGENTS.md — 8-Puzzle A* Solver

## Project Overview

An A* search solver for the classic 8-puzzle sliding tile problem, built with the **Tiferet** framework (configuration-driven Domain-Driven Design). Supports four admissible heuristics, arbitrary start/goal states, unsolvability detection, and both programmatic and CLI interfaces.

- **Repository:** https://github.com/Ashatz/ece-579-a-star-8-puzzle
- **Branch:** `master`
- **Python:** ≥ 3.10
- **Dependency:** `tiferet>=1.9.5` (only non-stdlib dep)

## Architecture

### How It Works

1. `App()` (Tiferet's `AppManagerContext`) loads interface and container configs from `app/configs/`.
2. `app.run('puzzle_solver', 'puzzle.solve', data={...})` resolves the `SolvePuzzle` domain event from the container and executes it.
3. `SolvePuzzle.execute()` parses input strings, validates states, checks solvability (inversion parity), selects the heuristic, runs A*, and returns formatted output.
4. The CLI interface (`puzzle_cli`) uses Tiferet's `CliContext` to parse command-line args and route to the same `puzzle.solve` feature.

### Project Structure

```
ece-579-a-star-8-puzzle/
├── puzzle_cli.py              # CLI entry point (loads puzzle_cli interface)
├── puzzle_run.py              # Benchmark runner (all 4 heuristics × test cases)
├── pyproject.toml             # Package config (only dep: tiferet>=1.9.5)
├── AGENTS.md                  # This file
├── README.md                  # User-facing docs
├── docs/
│   └── heuristics_guide.md    # Detailed heuristic explanations + benchmark results
└── app/
    ├── __init__.py            # Package docstring + __version__
    ├── events/
    │   ├── __init__.py
    │   ├── settings.py        # PuzzleEvent base class + PDB precomputation utilities
    │   └── puzzle.py          # SolvePuzzle domain event (A* + all heuristics)
    └── configs/
        ├── __init__.py
        ├── app.yml            # Interfaces: puzzle_solver, puzzle_cli
        ├── cli.yml            # CLI command/arg definitions
        ├── container.yml      # DI container: maps solve_puzzle_event → SolvePuzzle
        ├── error.yml          # Error definitions (INVALID_STATE, UNSOLVABLE_STATE, INVALID_HEURISTIC)
        ├── feature.yml        # Feature workflows (puzzle.solve + heuristic-specific variants)
        └── logging.yml        # Logging config
```

### Key Files

- **`app/events/settings.py`** — `PuzzleEvent` base class providing: `parse_state()` (string → flat int list), `verify_state()`, `is_solvable()` (inversion parity), `format_grid()`. Also contains PDB utilities: `ADJACENCY_3X3`, `_abstract_state()`, `_precompute_pdb()` (0-1 BFS), `_get_pdb_tables()` (lazy cache), `pattern_db_lookup()`.
- **`app/events/puzzle.py`** — `SolvePuzzle(PuzzleEvent)` domain event. Entry point is `execute(start, goal, heuristic, blank_symbol)`. Contains A* implementation (`_astar`), neighbor generation (`_get_neighbors`), path reconstruction (`_reconstruct_path`), and four heuristic methods: `_misplaced`, `_manhattan`, `_linear_conflict`, `_pattern_db`.
- **`app/configs/feature.yml`** — Defines `puzzle.solve` (generic), plus `puzzle.solve_manhattan`, `puzzle.solve_misplaced`, `puzzle.solve_linear_conflict`, `puzzle.solve_pattern_db` (each with hardcoded heuristic param).
- **`app/configs/cli.yml`** — CLI command `puzzle solve <start> [--goal] [--heuristic] [--blank-symbol]`.
- **`app/configs/container.yml`** — Single container attribute: `solve_puzzle_event` → `app.events.puzzle.SolvePuzzle`.
- **`app/configs/error.yml`** — Three error codes: `INVALID_STATE`, `UNSOLVABLE_STATE`, `INVALID_HEURISTIC`.

## State Representation

- **User-facing:** Comma or space-separated string with `*` for blank (e.g., `"2,8,3,1,6,4,7,*,5"`).
- **Internal:** Flat `List[int]` of 9 values (0 = blank), row-major order. Position `i` maps to row `i // 3`, col `i % 3`.
- **A* search:** States are `Tuple[int, ...]` for hashability. Heuristic methods accept `(state: Tuple[int, ...], goal: Tuple[int, ...])`.

## Heuristics

All four are admissible and consistent, guaranteeing optimal solutions:

- **`misplaced`** — Count of tiles not in goal position. Weakest.
- **`manhattan`** — Sum of taxicab distances per tile. Default.
- **`linear-conflict`** — Manhattan + 2 per reversed pair sharing a row/column goal line. ~30–50% fewer nodes than Manhattan.
- **`pattern-db`** — Additive PDB with two disjoint 4-tile patterns ({1,2,3,4} and {5,6,7,8}). Precomputed via 0-1 BFS (~15k entries each, ~50ms first use, cached per goal). ~85–95% fewer nodes than Manhattan.

Heuristic selection in `SolvePuzzle.execute()` uses a dict mapping heuristic name → instance method.

## Tiferet Framework Conventions

This project follows Tiferet's structured code style:

- **Artifact comments:** `# *** imports`, `# ** core` / `# ** app`, `# *** events`, `# ** event: <name>`, `# * method: <name>`.
- **Domain events:** Extend `DomainEvent` (via `PuzzleEvent`). Entry point is `execute(**kwargs)`. Use `self.verify()` for domain rule enforcement and `self.raise_error()` for direct errors.
- **YAML-driven config:** Interfaces in `app.yml`, DI container in `container.yml`, features in `feature.yml`, CLI in `cli.yml`, errors in `error.yml`.
- **Docstrings:** RST format with `:param`, `:type`, `:return`, `:rtype`.
- **Code snippets:** Each logical step is a separate snippet preceded by a comment line, with one empty line between snippets.

## Running

```bash
# Setup
python3.10 -m venv .venv && source .venv/bin/activate
pip install -e .

# CLI
python puzzle_cli.py puzzle solve "2,8,3,1,6,4,7,*,5" --goal "1,2,3,8,*,4,7,6,5" --heuristic manhattan

# Benchmark all heuristics
python puzzle_run.py
```

## Extending

### Adding a New Heuristic

1. Add the heuristic method to `SolvePuzzle` in `app/events/puzzle.py` with signature `(self, state: Tuple[int, ...], goal: Tuple[int, ...]) -> int`.
2. Add the method to the `heuristic_map` dict in `SolvePuzzle.execute()`.
3. Add the heuristic name to the `valid_heuristics` tuple in `execute()`.
4. Add a feature entry in `app/configs/feature.yml` with the heuristic param.
5. Add the choice to `app/configs/cli.yml` under `--heuristic` choices.
6. Update the `INVALID_HEURISTIC` message in `app/configs/error.yml`.
7. Add it to the `heuristics` list in `puzzle_run.py` for benchmarking.

### Adding a New Error

1. Add the error code and message to `app/configs/error.yml`.
2. Reference it via `self.verify(expr, 'ERROR_CODE', message, **kwargs)` or `self.raise_error('ERROR_CODE', message, **kwargs)` in the domain event.

### Adding a New Interface

1. Define the interface in `app/configs/app.yml` (see `puzzle_cli` for a `CliContext` example).
2. Load it via `app.load_interface('interface_id')` in a script.

## AI Collaboration

This project was developed in collaboration with **Grok 4** (xAI) for initial design and **Oz** (Warp AI agent) for full implementation, including linear conflict and pattern database heuristics, benchmark test collection, and documentation updates. All commits include `Co-Authored-By` attribution.
