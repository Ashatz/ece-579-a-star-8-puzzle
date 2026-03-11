# PuzzleStateParser Utility

**Module:** `app/utils/state.py`
**Class:** `PuzzleStateParser`
**Alias:** `State` (via `app/utils/__init__.py`)

## Overview

`PuzzleStateParser` provides static methods for parsing, validating, and formatting 8-puzzle states. It decouples state-handling logic from the domain event layer, making these operations available to any component without requiring a `DomainEvent` instance.

## State Representation

- **User-facing:** Comma-separated, space-separated, or contiguous 9-character string with `*` for the blank tile (e.g., `"1,2,3,4,5,6,7,8,*"`).
- **Internal:** Flat `List[int]` of 9 values where `0` represents the blank tile, in row-major order. Position `i` maps to row `i // 3`, column `i % 3`.

## Methods

### `parse_state(state_str: str) -> List[int]`

Parses a string into a flat integer list. Accepts three formats:

1. **Comma-separated:** `"1,2,3,4,5,6,7,8,*"` → `[1,2,3,4,5,6,7,8,0]`
2. **Space-separated:** `"1 2 3 4 5 6 7 8 *"` → `[1,2,3,4,5,6,7,8,0]`
3. **Contiguous (9 chars):** `"123456780"` → `[1,2,3,4,5,6,7,8,0]`

The `*` symbol is normalized to `0` before parsing. Raises `INVALID_STATE` if any token cannot be converted to an integer.

### `verify_state(state: List[int]) -> None`

Validates that a state contains exactly 9 elements with values 0–8, each appearing exactly once. Raises `INVALID_STATE` on failure — this catches wrong-length lists, out-of-range values, and duplicate tiles in a single check.

### `is_solvable(state: List[int], goal: List[int]) -> bool`

Determines whether a start state can reach a goal state by comparing **inversion parity**.

**Algorithm:** An *inversion* is a pair of non-blank tiles `(a, b)` where `a` appears before `b` in the flat list but `a > b`. For a 3×3 puzzle with no row parity constraint (blank moves freely), two states are reachable from each other if and only if they share the same inversion parity (both even or both odd).

The method counts inversions for both states and returns `True` if their parities match.

### `format_grid(state: List[int], blank_symbol: str = '*') -> str`

Formats a flat state as a human-readable 3×3 grid. Replaces `0` with `blank_symbol` and joins three rows with newlines.

**Example output:**
```
1 2 3
4 5 6
7 8 *
```

## Error Handling

All errors are raised via `RaiseError.execute()` from `tiferet.events`, producing `TiferetError` instances with structured error codes. The utility has no runtime dependency on the domain event layer beyond this static call.

- **`INVALID_STATE`** — Raised by `parse_state` (non-numeric input) and `verify_state` (invalid tile set).

## Usage

```python
from app.utils import State

# Parse and validate
state = State.parse_state('2,8,3,1,6,4,7,*,5')
State.verify_state(state)

# Check solvability
goal = State.parse_state('1,2,3,8,*,4,7,6,5')
if State.is_solvable(state, goal):
    print('Solvable!')

# Display
print(State.format_grid(state))
```
