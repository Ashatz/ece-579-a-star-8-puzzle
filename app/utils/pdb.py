# *** imports

# ** core
from collections import deque
from typing import Dict, List, Tuple

# ** app
from .search import ADJACENCY_3X3


# *** constants

# ** constant: pdb_tiles_1
PDB_TILES_1 = [1, 2, 3, 4]

# ** constant: pdb_tiles_2
PDB_TILES_2 = [5, 6, 7, 8]


# *** classes

# ** class: pdb_cache
_PDB_CACHE: Dict[Tuple[int, ...], Tuple[dict, dict]] = {}


# *** utils

# ** util: pattern_database
class PatternDatabase:
    '''
    Utility for precomputing and querying additive pattern databases
    for the 8-puzzle. Provides static methods for abstracting puzzle
    states into pattern-specific representations, precomputing distance
    tables via 0-1 BFS, lazily caching tables per goal state, and
    looking up the additive heuristic value from two disjoint tile
    patterns ({1,2,3,4} and {5,6,7,8}).
    '''

    # * method: abstract_state (static)
    @staticmethod
    def abstract_state(state, sorted_tiles: List[int]) -> Tuple[int, ...]:
        '''
        Extract an abstract state from a flat puzzle state for PDB lookup.
        Returns (blank_pos, pos_of_tile_1, pos_of_tile_2, ...).

        :param state: The flat puzzle state (list or tuple of 9 ints).
        :type state: list | tuple
        :param sorted_tiles: The pattern tile values in sorted order.
        :type sorted_tiles: List[int]
        :return: The abstract state tuple.
        :rtype: Tuple[int, ...]
        '''

        # Convert to list for index lookup.
        flat = list(state)

        # Extract blank position and pattern tile positions.
        blank_pos = flat.index(0)
        tile_positions = tuple(flat.index(t) for t in sorted_tiles)

        # Return the abstract state.
        return (blank_pos,) + tile_positions

    # * method: precompute (static)
    @staticmethod
    def precompute(tiles: set, goal: Tuple[int, ...]) -> Dict[Tuple[int, ...], int]:
        '''
        Precompute a pattern database via 0-1 BFS backward from the goal.
        Moves that displace pattern tiles cost 1; moves over non-pattern
        tiles cost 0.

        :param tiles: The set of tile values in the pattern.
        :type tiles: set
        :param goal: The goal state as a flat tuple of 9 ints.
        :type goal: Tuple[int, ...]
        :return: A mapping from abstract state to exact move cost.
        :rtype: Dict[Tuple[int, ...], int]
        '''

        # Build the sorted tile list for consistent key ordering.
        sorted_tiles = sorted(tiles)

        # Compute the goal abstract state.
        goal_abstract = PatternDatabase.abstract_state(goal, sorted_tiles)

        # Initialize the distance table and BFS queue.
        distances: Dict[Tuple[int, ...], int] = {goal_abstract: 0}
        queue = deque([(goal_abstract, 0)])

        # 0-1 BFS: cost-0 moves go to front, cost-1 moves go to back.
        while queue:
            state, dist = queue.popleft()

            # Skip if a shorter path was already found.
            if distances.get(state, float('inf')) < dist:
                continue

            blank_pos = state[0]
            tile_positions = list(state[1:])

            # Explore all adjacent positions for the blank.
            for neighbor_pos in ADJACENCY_3X3[blank_pos]:
                new_tile_positions = list(tile_positions)
                move_cost = 0

                # Check if the neighbor position holds a pattern tile.
                for i, pos in enumerate(tile_positions):
                    if pos == neighbor_pos:
                        new_tile_positions[i] = blank_pos
                        move_cost = 1
                        break

                new_cost = dist + move_cost
                new_state = (neighbor_pos,) + tuple(new_tile_positions)

                # Update if this is a new or shorter path.
                if new_state not in distances or new_cost < distances[new_state]:
                    distances[new_state] = new_cost
                    if move_cost == 0:
                        queue.appendleft((new_state, new_cost))
                    else:
                        queue.append((new_state, new_cost))

        # Return the completed distance table.
        return distances

    # * method: get_tables (static)
    @staticmethod
    def get_tables(goal: Tuple[int, ...]) -> Tuple[dict, dict]:
        '''
        Get (or lazily compute) PDB tables for a given goal state.

        :param goal: The goal state as a flat tuple of 9 ints.
        :type goal: Tuple[int, ...]
        :return: A pair of PDB lookup dicts (pattern1, pattern2).
        :rtype: Tuple[dict, dict]
        '''

        # Return cached tables if available.
        if goal in _PDB_CACHE:
            return _PDB_CACHE[goal]

        # Precompute both pattern databases.
        pdb1 = PatternDatabase.precompute({1, 2, 3, 4}, goal)
        pdb2 = PatternDatabase.precompute({5, 6, 7, 8}, goal)

        # Cache and return.
        _PDB_CACHE[goal] = (pdb1, pdb2)
        return pdb1, pdb2

    # * method: lookup (static)
    @staticmethod
    def lookup(state, goal) -> int:
        '''
        Look up the additive pattern database heuristic value.

        :param state: The current puzzle state as a flat list/tuple.
        :type state: list | tuple
        :param goal: The goal puzzle state as a flat list/tuple.
        :type goal: list | tuple
        :return: The sum of PDB lookups for both disjoint patterns.
        :rtype: int
        '''

        # Get the PDB tables for this goal.
        goal_tuple = tuple(goal)
        pdb1, pdb2 = PatternDatabase.get_tables(goal_tuple)

        # Look up abstract states for each pattern.
        abs1 = PatternDatabase.abstract_state(state, PDB_TILES_1)
        abs2 = PatternDatabase.abstract_state(state, PDB_TILES_2)

        # Sum the costs (0 fallback if abstract state not found).
        h1 = pdb1.get(abs1, 0)
        h2 = pdb2.get(abs2, 0)

        # Return the additive heuristic value.
        return h1 + h2
