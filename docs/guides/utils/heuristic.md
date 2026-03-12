# HeuristicCalculator Utility

**Module:** `app/utils/heuristic.py`  
**Class:** `HeuristicCalculator` (alias: `Heuristic`)  
**Import:** `from app.utils import HeuristicCalculator` or `from app.utils import Heuristic`

## Overview

`HeuristicCalculator` provides static methods for computing admissible heuristic values for the 8-puzzle. Each method accepts a current state and a goal state (both as flat integer lists of length 9, with 0 representing the blank tile) and returns a non-negative integer cost estimate. The four heuristics — misplaced tiles, Manhattan distance, linear conflict, and additive pattern database — range from weakest to strongest in pruning power, with stronger heuristics expanding fewer nodes at the cost of more computation per node.

All four heuristics are admissible (never overestimate the true cost) and consistent (satisfy the triangle inequality), guaranteeing optimal solutions when used with A* search.

## Heuristics

### Misplaced Tiles

**Method:** `misplaced(state, goal) -> int`

Counts the number of tiles not in their goal position, excluding the blank tile. This is the simplest admissible heuristic and provides the weakest pruning.

**Algorithm:**
1. For each position `i` in `[0, 8]`, check if `state[i] != goal[i]` and `state[i] != 0`.
2. Sum the count of mismatched tiles.

**Properties:**
- **Admissible:** Each misplaced tile requires at least one move to reach its goal position.
- **Consistent:** Moving one tile changes the misplaced count by at most ±1.
- **Weakness:** Ignores the distance each tile must travel, leading to many expanded nodes.

**Example:**
```
State:  [2, 8, 3, 1, 6, 4, 7, 0, 5]
Goal:   [1, 2, 3, 4, 5, 6, 7, 8, 0]
Result: 7 (all non-blank tiles are misplaced except none)
```

### Manhattan Distance

**Method:** `manhattan(state, goal) -> int`

Calculates the sum of taxicab (Manhattan) distances for every non-blank tile from its current position to its goal position on the 3×3 grid.

**Algorithm:**
1. Build a lookup map from tile value to its goal index.
2. For each non-blank tile at position `i`:
   - Compute current row/col: `i // 3`, `i % 3`.
   - Compute goal row/col from the lookup map.
   - Add `|current_row - goal_row| + |current_col - goal_col|` to the total.

**Properties:**
- **Admissible:** Each tile must travel at least its Manhattan distance (moves are orthogonal, one tile at a time).
- **Consistent:** A single move changes one tile's Manhattan distance by exactly ±1.
- **Strength:** Significantly stronger than misplaced tiles. The default heuristic for most 8-puzzle solvers.

**Example:**
```
State:  [1, 2, 3, 4, 5, 6, 7, 0, 8]
Goal:   [1, 2, 3, 4, 5, 6, 7, 8, 0]
Result: 1 (tile 8 is one position away)
```

### Linear Conflict

**Method:** `linear_conflict(state, goal) -> int`

Extends Manhattan distance by adding a +2 penalty for each pair of tiles that are in the same row or column as their goal positions but are reversed relative to each other. This captures the fact that resolving such a conflict requires at least two additional moves beyond what Manhattan distance accounts for.

**Algorithm:**
1. Compute the Manhattan distance as the base value.
2. For each row (0–2):
   - Collect tiles that are in their goal row (both current and goal positions share the same row).
   - For each pair, check if their current column order is reversed relative to their goal column order.
   - Add +2 per reversed pair.
3. Repeat for each column (0–2), checking row order reversals.

**Properties:**
- **Admissible:** The conflict penalty is exactly 2 per reversed pair (they must leave and re-enter the line), which is a provable lower bound.
- **Consistent:** Satisfies the triangle inequality since each move can resolve at most one conflict.
- **Dominance:** Always ≥ Manhattan distance, meaning it never expands more nodes than Manhattan. Typically reduces expanded nodes by 30–50%.

**Example:**
```
State:  [2, 1, 3, 4, 5, 6, 7, 8, 0]
Goal:   [1, 2, 3, 4, 5, 6, 7, 8, 0]
Manhattan: 2 (tile 1: 1 move, tile 2: 1 move)
Conflict:  +2 (tiles 1,2 in row 0, reversed)
Result:    4
```

### Additive Pattern Database

**Method:** `pattern_db(state, goal) -> int`

Delegates to `PatternDatabase.lookup()` to retrieve the additive heuristic value from two precomputed disjoint pattern databases. The patterns are `{1,2,3,4}` and `{5,6,7,8}`, each precomputed via 0-1 BFS. The heuristic value is the sum of exact move costs for each pattern independently.

**Algorithm:**
1. Ensure PDB tables are computed for the goal (lazily cached on first use).
2. Abstract the current state into each pattern's representation.
3. Look up the exact cost for each pattern in its precomputed table.
4. Sum the two costs.

**Properties:**
- **Admissible:** Each pattern's cost is exact for its tile subset. Because the patterns are disjoint (no shared tiles), their sum is a valid lower bound on the total cost.
- **Consistent:** Follows from the disjointness of the patterns and the admissibility of each individual PDB.
- **Dominance:** Typically the strongest of the four heuristics, reducing expanded nodes by 85–95% compared to Manhattan.
- **Trade-off:** First use incurs ~50ms precomputation per goal state (cached for subsequent lookups). Each lookup is O(1) after precomputation.

See the [PatternDatabase guide](pdb.md) for details on the precomputation algorithm, abstract state representation, and caching behavior.

## Admissibility and Consistency

All four heuristics guarantee optimal solutions when paired with A*:

- **Admissibility** means `h(n) ≤ h*(n)` for all states `n`, where `h*(n)` is the true optimal cost. This ensures A* never skips the optimal path.
- **Consistency** (monotonicity) means `h(n) ≤ cost(n, n') + h(n')` for every successor `n'`. This ensures each state is expanded at most once, making A* efficient with a closed set.

**Dominance ordering** (weaker to stronger):
```
misplaced ≤ manhattan ≤ linear_conflict ≤ pattern_db
```

A stronger heuristic never expands more nodes than a weaker one, but may require more computation per node.

## Usage by Domain Events

The `SolvePuzzle` domain event selects a heuristic by name and passes the corresponding static method to `AStarSearch.search()` as a callable:

```python
from app.utils import Heuristic, AStar

# Heuristic map used in SolvePuzzle.execute().
heuristic_map = {
    'misplaced': Heuristic.misplaced,
    'manhattan': Heuristic.manhattan,
    'linear-conflict': Heuristic.linear_conflict,
    'pattern-db': Heuristic.pattern_db,
}

# Select and run.
heuristic_fn = heuristic_map['manhattan']
path, nodes_expanded = AStar.search(start_state, goal_state, heuristic_fn)
```

This decoupling allows heuristics and the search algorithm to be tested and extended independently.

## Testing

Tests are located in `app/utils/tests/test_heuristic.py` and cover:
- **Misplaced:** Goal returns 0, non-goal returns positive, one-move state returns 1.
- **Manhattan:** Goal returns 0, non-goal returns positive, one-move state returns 1, admissibility against known optimal cost.
- **Linear conflict:** Equals Manhattan when no conflicts exist, exceeds Manhattan by exactly +2 per reversed pair, goal returns 0, dominance over Manhattan.
- **Pattern DB:** Goal returns 0, non-goal returns positive, admissibility against known optimal cost.

Run tests with:
```bash
pytest app/utils/tests/test_heuristic.py -v
```
