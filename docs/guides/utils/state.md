# PuzzleStateParser Utility

**Module:** `app/utils/state.py`  
**Class:** `PuzzleStateParser` (alias: `State`)  
**Import:** `from app.utils import PuzzleStateParser` or `from app.utils import State`

## Overview

`PuzzleStateParser` provides static methods for converting user-facing 8-puzzle state strings into internal integer lists, validating state correctness, checking solvability via inversion parity, and pretty-printing states as 3×3 grids. It is a pure infrastructure utility with no domain event dependencies — errors are raised via `RaiseError.execute()` from the Tiferet framework.

## State Representation

### User-Facing Format
States are provided as strings in one of three formats:
- **Comma-separated:** `"2,8,3,1,6,4,7,*,5"`
- **Space-separated:** `"2 8 3 1 6 4 7 * 5"`
- **Contiguous:** `"283164705"` (9 characters, digits only)

The blank tile can be represented as `*` or `0`.

### Internal Format
Internally, a state is a flat `List[int]` of 9 values where `0` represents the blank tile. Positions are in row-major order:

```
Index:  0  1  2
        3  4  5
        6  7  8
```

Position `i` maps to row `i // 3`, column `i % 3`.

## Methods

### `parse_state(state_str: str) -> List[int]`
Converts a user-facing string into the internal integer list. Steps:
1. Replace `*` with `0` to normalize the blank symbol.
2. Split on commas or whitespace. If the result is a single 9-character token, split by character (contiguous format).
3. Convert each token to `int`. Raises `INVALID_STATE` on non-numeric input.

### `verify_state(state: List[int]) -> None`
Validates that a state is well-formed:
- Exactly 9 elements.
- Contains each value from 0 through 8 exactly once.

Raises `INVALID_STATE` if either condition fails.

### `is_solvable(state: List[int], goal: List[int]) -> bool`
Determines whether the puzzle is solvable by comparing **inversion parities** of the start and goal states.

**Algorithm — Inversion Parity:**
An *inversion* is a pair of non-blank tiles `(a, b)` where `a` appears before `b` in the flat list but `a > b`. For a 3×3 sliding puzzle, a start state is reachable from the goal if and only if both have the same inversion parity (both even or both odd).

1. Count inversions in `state` (ignoring tile 0).
2. Count inversions in `goal` (ignoring tile 0).
3. Return `True` if both counts have the same parity (`% 2`).

This check runs in O(n²) where n = 8 (non-blank tiles), which is negligible for the 8-puzzle.

### `format_grid(state: List[int], blank_symbol: str = '*') -> str`
Renders a state as a human-readable 3×3 grid string. Each row is space-separated, rows are newline-separated. The blank tile (value 0) is displayed using `blank_symbol` (default `*`).

**Example output** for `[1, 2, 3, 4, 5, 6, 7, 8, 0]`:
```
1 2 3
4 5 6
7 8 *
```

## Error Handling

All errors are raised via `RaiseError.execute()` with structured error codes defined in `app/configs/error.yml`:

- **`INVALID_STATE`** — Raised by `parse_state` (non-numeric input) and `verify_state` (wrong length or duplicate tiles).

## Testing

Tests are located in `app/utils/tests/test_state.py` and cover:
- Parsing all three input formats plus blank symbol normalization.
- Invalid input detection.
- State validation (valid, wrong length, duplicate tiles).
- Solvability detection (solvable and unsolvable configurations).
- Grid formatting with default and custom blank symbols.

Run tests with:
```bash
pytest app/utils/tests/test_state.py -v
```
