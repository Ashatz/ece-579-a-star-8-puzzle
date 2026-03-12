# AStarSearch Utility

**Module:** `app/utils/search.py`  
**Class:** `AStarSearch` (alias: `AStar`)  
**Import:** `from app.utils import AStarSearch` or `from app.utils import AStar`

## Overview

`AStarSearch` provides static methods for solving the 8-puzzle using the A* search algorithm. It encapsulates the search loop, neighbor generation via blank-tile swaps on a 3×3 grid, and solution path reconstruction. The utility is a pure computational infrastructure component with no domain event dependencies — it accepts a heuristic function as a callable parameter, making it agnostic to the specific heuristic used.

This module also exports the `ADJACENCY_3X3` constant, a precomputed adjacency map for the 3×3 grid used by both neighbor generation and pattern database precomputation.

## The A* Algorithm

A* is an informed graph search algorithm that finds the shortest path from a start state to a goal state using a combination of actual cost and heuristic estimate.

### Core Concepts

- **g(n):** The actual cost (number of moves) from the start to state `n`.
- **h(n):** A heuristic estimate of the cost from state `n` to the goal. Must be admissible (never overestimates) to guarantee optimality.
- **f(n) = g(n) + h(n):** The estimated total cost through state `n`.

### Algorithm Steps

1. **Initialize:** Place the start state into a priority queue (open set) ordered by `f`. Set `g(start) = 0`.
2. **Expand:** Pop the state with the lowest `f` from the open set.
3. **Goal check:** If the current state is the goal, reconstruct and return the path.
4. **Generate neighbors:** For each neighbor of the current state:
   - Skip if already in the closed set (visited).
   - Compute `tentative_g = g(current) + 1`.
   - If this is a new or shorter path to the neighbor, update `g`, compute `f = g + h`, and push to the open set.
5. **Repeat** until the goal is found or the open set is empty.

### Tie-Breaking

When multiple states share the same `f`-score, a monotonically increasing counter is used as a tie-breaker to ensure FIFO ordering among equal-priority states. This prevents tuple comparison errors when states are not directly comparable.

### Optimality Guarantee

A* is optimal when the heuristic is admissible (h never overestimates) and consistent (h satisfies the triangle inequality). All four heuristics provided by the puzzle project (misplaced, Manhattan, linear conflict, pattern database) are both admissible and consistent.

## ADJACENCY_3X3 Constant

A precomputed dictionary mapping each position (0–8) on the 3×3 grid to its list of adjacent positions:

```
Position layout:
  0  1  2
  3  4  5
  6  7  8

ADJACENCY_3X3 = {
    0: [1, 3],       1: [0, 2, 4],    2: [1, 5],
    3: [0, 4, 6],    4: [1, 3, 5, 7], 5: [2, 4, 8],
    6: [3, 7],       7: [4, 6, 8],    8: [5, 7],
}
```

Corners have 2 neighbors, edges have 3, and the center has 4. This map is used by `get_neighbors` for move generation and imported by `PatternDatabase` for PDB precomputation.

## Methods

### `search(start, goal, heuristic_fn) -> Tuple[List[List[int]], int]`

Runs the full A* search from `start` to `goal` using the provided heuristic function.

**Parameters:**
- `start: List[int]` — The initial state (flat list of 9 ints, 0 = blank).
- `goal: List[int]` — The goal state.
- `heuristic_fn: Callable[[List[int], List[int]], int]` — A function that takes `(state, goal)` and returns the heuristic estimate.

**Returns:** A tuple of `(path, nodes_expanded)` where `path` is a list of states from start to goal (each as `List[int]`), and `nodes_expanded` is the number of states removed from the open set.

**Implementation details:**
- States are converted to tuples internally for hashability in sets and dicts.
- Uses Python's `heapq` module for the priority queue.
- Falls back to returning `[start]` with the expanded count if no solution is found (should not occur if solvability was checked beforehand).

### `get_neighbors(state) -> List[Tuple[int, ...]]`

Generates all valid neighbor states by swapping the blank tile (value 0) with each adjacent tile.

**Parameters:**
- `state: Tuple[int, ...]` — The current state as a tuple.

**Returns:** A list of neighbor state tuples. The number of neighbors depends on the blank's position: 2 (corner), 3 (edge), or 4 (center).

**Algorithm:**
1. Find the blank tile's index in the state.
2. Look up adjacent positions from `ADJACENCY_3X3`.
3. For each adjacent position, create a copy of the state with the blank and adjacent tile swapped.

### `reconstruct_path(parents, current) -> List[List[int]]`

Traces the parent map backward from the goal state to the start to build the solution path.

**Parameters:**
- `parents: Dict[Tuple[int, ...], Tuple[int, ...] | None]` — A mapping from each state to its predecessor (`None` for the start).
- `current: Tuple[int, ...]` — The goal state to trace back from.

**Returns:** The solution path as a list of states in start-to-goal order (each as `List[int]`).

## Usage by Domain Events

The `SolvePuzzle` domain event delegates to `AStarSearch.search()` for the core search logic. The heuristic function is selected from `HeuristicCalculator` and passed as a callable:

```python
from app.utils import AStar, Heuristic

# Select heuristic.
heuristic_fn = Heuristic.manhattan

# Run A* search.
path, nodes_expanded = AStar.search(start_state, goal_state, heuristic_fn)
```

This decoupling allows the search algorithm to remain independent of heuristic implementation, and both can be tested and extended independently.

## Testing

Tests are located in `app/utils/tests/test_search.py` and cover:
- Neighbor generation at center, corner, and edge positions.
- Path reconstruction from a known parent map.
- Search with start equal to goal (zero moves).
- Search with a one-move puzzle.
- Search with a known multi-move configuration (verified optimal).

A trivial misplaced-tiles lambda is used as the heuristic in tests, keeping the search tests independent of the `HeuristicCalculator` utility.

Run tests with:
```bash
pytest app/utils/tests/test_search.py -v
```
