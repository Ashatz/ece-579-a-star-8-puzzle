# PatternDatabase Utility

**Module:** `app/utils/pdb.py`  
**Class:** `PatternDatabase` (alias: `PDB`)  
**Import:** `from app.utils import PatternDatabase` or `from app.utils import PDB`

## Overview

`PatternDatabase` provides static methods for precomputing and querying additive pattern databases (PDBs) for the 8-puzzle. It encapsulates abstract state extraction, 0-1 BFS precomputation, lazy caching of distance tables per goal state, and additive heuristic lookup from two disjoint tile patterns. The utility is a stateful computational infrastructure component — it maintains a module-level cache of precomputed tables — with no domain event dependencies.

This module also exports the `PDB_TILES_1` and `PDB_TILES_2` constants, which define the two disjoint 4-tile patterns used for additive PDB lookup.

## Additive Pattern Databases

A pattern database is a precomputed lookup table that stores the exact minimum number of moves required to place a subset of tiles (a "pattern") into their goal positions, ignoring all other tiles. By decomposing the 8-puzzle into disjoint tile subsets and summing their independent PDB values, we obtain an admissible and consistent heuristic that is significantly more informed than Manhattan distance alone.

### Disjoint Pattern Decomposition

The 8 non-blank tiles are split into two disjoint groups:

- **Pattern 1:** `{1, 2, 3, 4}` — the first four tiles.
- **Pattern 2:** `{5, 6, 7, 8}` — the last four tiles.

Because these patterns share no tiles, their costs are independent and can be safely summed without violating admissibility. The additive heuristic value `h(s) = pdb1(s) + pdb2(s)` never overestimates the true cost, making it both admissible and consistent.

### Why Two 4-Tile Patterns?

A single 8-tile PDB would be optimal in accuracy but prohibitively large (9 × 9! / 1 ≈ 3.3M entries). Two 4-tile patterns produce approximately 15,000 entries each (9 × P(8,4) = 9 × 1680 ≈ 15,120), fitting comfortably in memory. The additive combination typically yields ~85–95% fewer node expansions than Manhattan distance.

## Abstract State Representation

An abstract state captures only the positions relevant to a specific pattern, discarding information about non-pattern tiles. For a 4-tile pattern, the abstract state is a 5-tuple:

```
(blank_pos, pos_of_tile_a, pos_of_tile_b, pos_of_tile_c, pos_of_tile_d)
```

Where:
- `blank_pos` — the position (0–8) of the blank tile. The blank's position is always tracked because it participates in every move.
- `pos_of_tile_*` — the positions of the pattern tiles, in sorted order by tile value.

**Example:** For state `[2, 8, 3, 1, 6, 4, 7, 0, 5]` and pattern `{1, 2, 3, 4}`:
- Blank (0) is at position 7.
- Tile 1 is at position 3, tile 2 at 0, tile 3 at 2, tile 4 at 5.
- Abstract state: `(7, 3, 0, 2, 5)`.

## 0-1 BFS Precomputation

The PDB is precomputed via a backward 0-1 BFS (zero-one breadth-first search) starting from the goal's abstract state. This is a variant of Dijkstra's algorithm optimized for graphs where edge weights are restricted to 0 or 1.

### Algorithm

1. **Initialize:** Set the goal abstract state's distance to 0. Push it to the front of a deque.
2. **Dequeue:** Pop the front state from the deque.
3. **Expand:** For each adjacent position of the blank:
   - If the adjacent position holds a **pattern tile**, moving it costs **1** (the tile is displaced). Swap the blank and tile positions in the abstract state.
   - If the adjacent position holds a **non-pattern tile**, moving it costs **0** (irrelevant tile). Only the blank position changes in the abstract state.
4. **Enqueue by cost:**
   - Cost-0 moves → push to the **front** of the deque (explored sooner).
   - Cost-1 moves → push to the **back** of the deque (explored later).
5. **Update:** Record the new state's distance only if it is shorter than any previously found path.
6. **Repeat** until the deque is empty.

### Why 0-1 BFS?

Standard BFS assumes uniform edge costs. In PDB precomputation, moves involving non-pattern tiles are "free" (cost 0) because we only count moves that displace pattern tiles. The 0-1 BFS deque handles this naturally: cost-0 moves are explored at the same depth level, while cost-1 moves are deferred, preserving optimality without the overhead of a full priority queue.

### Adjacency Map

The 0-1 BFS uses the `ADJACENCY_3X3` constant from `app.utils.search`, which maps each position on the 3×3 grid to its list of adjacent positions. This is the same adjacency map used by `AStarSearch.get_neighbors()`.

## Lazy Caching

PDB tables are expensive to compute (~50ms for both patterns on first use) but are reused across all heuristic lookups for a given goal state. The `get_tables()` method implements lazy caching:

1. Check the module-level `_PDB_CACHE` dict for the goal tuple.
2. If cached, return immediately.
3. Otherwise, precompute both pattern tables, store in the cache, and return.

The cache key is the goal state as a tuple (hashable). Different goal states produce independent PDB tables. The cache persists for the lifetime of the Python process.

## Constants

### `PDB_TILES_1`

```python
PDB_TILES_1 = [1, 2, 3, 4]
```

The first disjoint pattern: tiles 1 through 4.

### `PDB_TILES_2`

```python
PDB_TILES_2 = [5, 6, 7, 8]
```

The second disjoint pattern: tiles 5 through 8.

### `_PDB_CACHE`

```python
_PDB_CACHE: Dict[Tuple[int, ...], Tuple[dict, dict]] = {}
```

Module-level cache mapping goal state tuples to precomputed `(pdb1, pdb2)` table pairs.

## Methods

### `abstract_state(state, sorted_tiles) -> Tuple[int, ...]`

Extracts the abstract state tuple from a full puzzle state for a given tile pattern.

**Parameters:**
- `state: list | tuple` — The flat puzzle state (9 ints, 0 = blank).
- `sorted_tiles: List[int]` — The pattern tile values in sorted order.

**Returns:** A tuple of `(blank_pos, tile_pos_1, tile_pos_2, ...)` representing positions of the blank and each pattern tile.

### `precompute(tiles, goal) -> Dict[Tuple[int, ...], int]`

Precomputes a pattern database via 0-1 BFS backward from the goal state.

**Parameters:**
- `tiles: set` — The set of tile values in the pattern (e.g., `{1, 2, 3, 4}`).
- `goal: Tuple[int, ...]` — The goal state as a flat tuple of 9 ints.

**Returns:** A dictionary mapping abstract state tuples to their exact minimum move costs.

**Implementation details:**
- Sorts the tile set for consistent key ordering in abstract states.
- Uses a `collections.deque` for the 0-1 BFS queue.
- Explores all reachable abstract states from the goal backward, producing a complete distance table.

### `get_tables(goal) -> Tuple[dict, dict]`

Returns the pair of PDB lookup tables for a goal state, computing and caching them if necessary.

**Parameters:**
- `goal: Tuple[int, ...]` — The goal state as a flat tuple of 9 ints.

**Returns:** A tuple `(pdb1, pdb2)` where `pdb1` is the table for pattern `{1,2,3,4}` and `pdb2` for `{5,6,7,8}`.

### `lookup(state, goal) -> int`

Computes the additive PDB heuristic value by summing lookups from both pattern tables.

**Parameters:**
- `state: list | tuple` — The current puzzle state.
- `goal: list | tuple` — The goal puzzle state.

**Returns:** The sum of the two pattern database lookups. Returns 0 for the goal state. Falls back to 0 for any abstract state not found in the tables (should not occur for valid states).

## Usage by Domain Events

The `SolvePuzzle` domain event (and the `HeuristicCalculator` utility) delegates to `PatternDatabase.lookup()` for the pattern database heuristic:

```python
from app.utils import PDB

# Direct lookup.
h_value = PDB.lookup(current_state, goal_state)
```

The `HeuristicCalculator.pattern_db()` method wraps this call, providing a uniform interface alongside the other heuristics (misplaced, Manhattan, linear conflict).

## Testing

Tests are located in `app/utils/tests/test_pdb.py` and cover:
- Abstract state extraction for both patterns and scrambled states.
- Precomputation goal entry (distance 0 at goal).
- Precomputation produces a non-trivial table size (>1000 entries).
- `get_tables` returns non-empty dict pairs.
- `get_tables` caching (same object references on repeated calls).
- Lookup returns 0 for the goal state.
- Lookup returns a positive value for non-goal states.
- Admissibility check (heuristic ≤ known optimal solution length).

Run tests with:
```bash
pytest app/utils/tests/test_pdb.py -v
```
