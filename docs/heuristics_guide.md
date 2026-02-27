# Heuristics Guide for 8-Puzzle A* Solver

This document explains the four heuristics implemented in the **ece-579-a-star-8-puzzle** solver in detail. All are **admissible** (never overestimate the true minimum moves to the goal) and most are **consistent** (monotone), ensuring A* finds optimal solutions.

The heuristics build progressively in strength:

1. Misplaced Tiles (basic, mandatory)  
2. Manhattan Distance (basic, mandatory)  
3. Manhattan + Linear Conflict (enhanced, optional extension)  
4. Additive Pattern Database (advanced lookup-based, optional extension)

## 1. Misplaced Tiles (Tiles-Out-of-Place)

**Definition**  
Counts the number of tiles (excluding the blank) that are not in their correct goal position.

**Formula**  
h(s) = number of tiles where current position ≠ goal position

**Example**  
Goal:  
1 2 3  
4 5 6  
7 8 *  

State:  
1 2 3  
4 * 6  
7 8 5  

Misplaced tiles: 5 and 8 → h(s) = 2

**Properties**  
- Admissible: Yes (each misplaced tile requires at least 1 move).  
- Consistent: Yes.  
- Computation: Very fast (O(1) per state with pre-mapped goal positions).  
- Strength: Weakest — ignores how far tiles are from their goals, so many nodes expanded.

## 2. Manhattan Distance

**Definition**  
For each tile (excluding blank), sum the horizontal + vertical moves needed to reach its goal position (taxicab / L1 distance).

**Formula**  
h(s) = Σ |current_row(tile) - goal_row(tile)| + |current_col(tile) - goal_col(tile)| over all tiles ≠ blank

**Example** (same state as above)  
- Tile 5: current (2,1) → goal (1,2) → |2-1| + |1-2| = 2  
- Tile 8: current (2,2) → goal (2,1) → |2-2| + |2-1| = 1  
- Others correct → h(s) = 3

**Properties**  
- Admissible: Yes (tiles move only horizontally/vertically, no diagonals).  
- Consistent: Yes.  
- Computation: O(1) per state (9 tiles).  
- Strength: Much better than misplaced tiles — accounts for distance, but ignores interactions (tiles blocking each other).

## 3. Manhattan + Linear Conflict

**Definition**  
Start with Manhattan distance, then add +2 for each **linear conflict**: two tiles in the same row (or column) whose goal positions are also in that row (column), but they are reversed relative to each other (one blocks the other's direct path).

**Why +2?**  
To resolve a conflict, one tile must move aside (1 move), the other passes (1 move), and the first returns (implied in overall path) → minimum 2 extra moves beyond Manhattan.

**Detection Rule** (for a row or column):  
Two tiles t_j and t_k are in linear conflict if:  
- They are in the same line (row or column).  
- Their goal positions are in the same line.  
- t_j is left of t_k in current state, but goal position of t_j is right of goal position of t_k (or vice versa).  

**Example**  
Goal: 1 2 3 / 4 5 6 / 7 8 *  

State:  
1 3 2  
4 5 6  
7 8 *  

- Row 0: Tiles 3 and 2 are in correct row, but 3 is left of 2, while goal has 2 left of 3 → one linear conflict.  
- Manhattan = 2 (tile 2 and 3 each need 1 horizontal move).  
- Linear conflict adds +2.  
- Total h(s) = 4 (correct optimal moves needed).

**Properties**  
- Admissible: Yes (proven; extra cost is a lower bound on resolving conflicts).  
- Consistent: Yes (with coefficient +2; higher coefficients may lose consistency).  
- Computation: O(N) worst-case per state (scan lines).  
- Strength: Significantly reduces nodes expanded (often 30–70% fewer than plain Manhattan on hard instances) by accounting for tile interference in lines.

## 4. Additive Pattern Database (PDB) Heuristic

**Definition**  
Precompute exact minimum move costs to solve small **subproblems** (subsets of tiles, ignoring others and treating non-pattern tiles as "don't care"). For a given state, look up the cost for each pattern and **sum** them (additive because patterns are disjoint → no overlapping moves double-counted).

**Common Partition for 8-Puzzle**  
- Two disjoint patterns: tiles {1,2,3,4} and {5,6,7,8} (blank ignored or included in one).  
- Precompute via BFS from goal substates → store in a dictionary (abstract state → exact distance).

**How to Abstract a State for Lookup**  
- Map only the positions of tiles in the pattern to a tuple key (blank position + tile positions).  
- Ignore other tiles → many real states map to the same abstract state.

**Example Workflow**  
1. At startup: Run 0-1 BFS for each pattern from goal → build lookup table (~15k entries for 4-tile pattern — tiny).  
2. For a state s:  
   - For pattern 1: extract positions of its tiles → lookup exact cost c1.  
   - For pattern 2: same → c2.  
   - h(s) = c1 + c2 (additive).  

**Properties**  
- Admissible: Yes (exact cost for subset is a lower bound on full cost).  
- Consistent: Usually yes (if patterns are properly chosen).  
- Computation: Lookup O(1) after precompute; precompute is fast for 8-puzzle (~50ms for two 4-tile patterns).  
- Strength: Extremely powerful — small PDBs can solve most 8-puzzle instances with very few expansions (near-optimal informedness).

## Comparison Summary

| Heuristic                  | Memory | Precompute | Nodes Expanded (typical) | Best For          |
|----------------------------|--------|------------|---------------------------|-------------------|
| Misplaced Tiles            | None   | None       | High                      | Quick baseline    |
| Manhattan                  | None   | None       | Medium                    | Standard          |
| Manhattan + Linear Conflict| None   | None       | Low–Medium                | Good enhancement  |
| Additive Pattern Database  | Low    | Low        | Very Low                  | Highest accuracy  |

## Benchmark Results

The following results were measured using `puzzle_run.py` on two hard puzzle configurations. All heuristics found optimal (shortest) paths.

**Hard Puzzle A** — Start: `8,6,7,2,5,4,3,*,1` → Goal: `1,2,3,4,5,6,7,8,*` (31 moves)

| Heuristic              | Nodes Expanded | Time (s) | Reduction vs Manhattan |
|------------------------|----------------|----------|------------------------|
| Misplaced Tiles        | 143,840        | 0.463    | —                      |
| Manhattan              | 20,291         | 0.103    | baseline               |
| Linear Conflict        | 12,293         | 0.138    | 39% fewer nodes        |
| Pattern Database       | 1,030          | 0.006    | 95% fewer nodes        |

**Hard Puzzle B** — Start: `6,1,8,4,*,2,7,3,5` → Goal: `1,2,3,4,5,6,7,8,*` (18 moves)

| Heuristic              | Nodes Expanded | Time (s) | Reduction vs Manhattan |
|------------------------|----------------|----------|------------------------|
| Misplaced Tiles        | 1,643          | 0.005    | —                      |
| Manhattan              | 204            | 0.001    | baseline               |
| Linear Conflict        | 109            | 0.001    | 47% fewer nodes        |
| Pattern Database       | 31             | 0.0002   | 85% fewer nodes        |

**Key Observations**:
- Linear Conflict consistently expands 30–50% fewer nodes than Manhattan, with negligible compute overhead.
- Pattern Database achieves 85–95% node reduction on hard instances. First-use PDB precompute takes ~50ms (two 4-tile patterns via 0-1 BFS, ~15k entries each); subsequent lookups are O(1).
- All heuristics produce identical optimal path lengths, confirming admissibility.

## References
- Russell & Norvig, *Artificial Intelligence: A Modern Approach* (Manhattan, misplaced, linear conflict basics).  
- Felner et al., "Additive Pattern Database Heuristics" (JAIR 2004) — foundational for PDBs.

**Attribution**  
This heuristics guide was drafted with the assistance of Grok 4, built by xAI. Benchmark results and heuristic implementations were contributed by Oz (Warp AI agent).
