# *** imports

# ** core
from collections import deque
from typing import Dict, List, Tuple

# ** infra
from tiferet.events import *


# *** constants

# ** constant: adjacency_3x3
ADJACENCY_3X3: Dict[int, List[int]] = {
    0: [1, 3],
    1: [0, 2, 4],
    2: [1, 5],
    3: [0, 4, 6],
    4: [1, 3, 5, 7],
    5: [2, 4, 8],
    6: [3, 7],
    7: [4, 6, 8],
    8: [5, 7],
}

# ** constant: pdb_tiles_1
_PDB_TILES_1 = [1, 2, 3, 4]

# ** constant: pdb_tiles_2
_PDB_TILES_2 = [5, 6, 7, 8]

# ** constant: pdb_cache
_PDB_CACHE: Dict[Tuple[int, ...], Tuple[dict, dict]] = {}


# *** classes

# ** class: pdb_functions

# * method: _abstract_state
def _abstract_state(state, sorted_tiles: List[int]) -> Tuple[int, ...]:
    '''
    Extract an abstract state for a given tile pattern.

    :param state: The full puzzle state (tuple or list).
    :type state: tuple or list
    :param sorted_tiles: The tile values in this pattern.
    :type sorted_tiles: List[int]
    :return: A tuple of (blank_pos, pos_of_tile_1, pos_of_tile_2, ...).
    :rtype: Tuple[int, ...]
    '''

    # Find the blank position.
    blank_pos = list(state).index(0)

    # Find positions of each pattern tile.
    tile_positions = tuple(
        list(state).index(t) for t in sorted_tiles
    )

    # Return the abstract state.
    return (blank_pos,) + tile_positions


# * method: _precompute_pdb
def _precompute_pdb(tiles: set, goal: Tuple[int, ...]) -> Dict[Tuple[int, ...], int]:
    '''
    Precompute a pattern database via backward 0-1 BFS from the goal.

    :param tiles: The set of tile values in this pattern.
    :type tiles: set
    :param goal: The goal state as a tuple.
    :type goal: Tuple[int, ...]
    :return: A mapping from abstract state to exact move cost.
    :rtype: Dict[Tuple[int, ...], int]
    '''

    # Build the sorted tile list for abstract state extraction.
    sorted_tiles = sorted(tiles)

    # Compute the goal's abstract state.
    goal_abstract = _abstract_state(goal, sorted_tiles)

    # Initialize BFS with the goal abstract state at cost 0.
    pdb: Dict[Tuple[int, ...], int] = {goal_abstract: 0}
    dq = deque([(goal_abstract, 0)])

    # Run 0-1 BFS.
    while dq:

        # Pop the next abstract state.
        current, cost = dq.popleft()
        blank_pos = current[0]

        # Reconstruct the abstract tile positions.
        tile_positions = {sorted_tiles[i]: current[i + 1] for i in range(len(sorted_tiles))}

        # Try each neighbor of the blank.
        for neighbor_pos in ADJACENCY_3X3[blank_pos]:

            # Determine which tile (if any) occupies the neighbor position.
            moved_tile = None
            for t, p in tile_positions.items():
                if p == neighbor_pos:
                    moved_tile = t
                    break

            # Build the new abstract state after swapping blank with neighbor.
            if moved_tile is not None:
                # Pattern tile moves: cost 1.
                new_positions = dict(tile_positions)
                new_positions[moved_tile] = blank_pos
                new_abstract = (neighbor_pos,) + tuple(
                    new_positions[t] for t in sorted_tiles
                )
                move_cost = 1
            else:
                # Non-pattern tile moves: cost 0.
                new_abstract = (neighbor_pos,) + current[1:]
                move_cost = 0

            # Record if this abstract state hasn't been seen.
            new_total = cost + move_cost
            if new_abstract not in pdb:
                pdb[new_abstract] = new_total
                if move_cost == 0:
                    dq.appendleft((new_abstract, new_total))
                else:
                    dq.append((new_abstract, new_total))

    # Return the precomputed PDB.
    return pdb


# * method: _get_pdb_tables
def _get_pdb_tables(goal: Tuple[int, ...]) -> Tuple[dict, dict]:
    '''
    Return cached PDB tables for the goal, computing lazily on first access.

    :param goal: The goal state as a tuple.
    :type goal: Tuple[int, ...]
    :return: A pair of PDB dicts (one per tile pattern).
    :rtype: Tuple[dict, dict]
    '''

    # Check the cache first.
    if goal not in _PDB_CACHE:

        # Precompute both pattern databases.
        pdb1 = _precompute_pdb(set(_PDB_TILES_1), goal)
        pdb2 = _precompute_pdb(set(_PDB_TILES_2), goal)
        _PDB_CACHE[goal] = (pdb1, pdb2)

    # Return the cached tables.
    return _PDB_CACHE[goal]


# * method: pattern_db_lookup
def pattern_db_lookup(state, goal) -> int:
    '''
    Look up the additive pattern database heuristic value for a state.

    :param state: The current puzzle state.
    :type state: tuple or list
    :param goal: The goal puzzle state.
    :type goal: tuple or list
    :return: The sum of both pattern costs.
    :rtype: int
    '''

    # Ensure tuples for cache key.
    goal_tuple = tuple(goal)
    state_tuple = tuple(state)

    # Get the PDB tables for this goal.
    pdb1, pdb2 = _get_pdb_tables(goal_tuple)

    # Look up both abstract states and return their sum.
    abs1 = _abstract_state(state_tuple, _PDB_TILES_1)
    abs2 = _abstract_state(state_tuple, _PDB_TILES_2)

    # Return the additive heuristic value.
    return pdb1.get(abs1, 0) + pdb2.get(abs2, 0)


# *** events

# ** event: puzzle_event
class PuzzleEvent(DomainEvent):
    '''
    Base domain event for 8-puzzle operations.
    Provides shared utility methods for state parsing, validation,
    solvability checking, and grid formatting.
    '''

    # * method: parse_state
    def parse_state(self, state_str: str) -> List[int]:
        '''
        Parse a string representation of a puzzle state into a flat list of integers.

        :param state_str: The string representation of the puzzle state.
        :type state_str: str
        :return: A flat list of 9 integers representing the puzzle state.
        :rtype: List[int]
        '''

        # Normalize the blank symbol to 0.
        normalized = state_str.replace('*', '0')

        # Try splitting on commas first.
        if ',' in normalized:
            tokens = [t.strip() for t in normalized.split(',')]
        # Try splitting on whitespace.
        elif ' ' in normalized:
            tokens = normalized.split()
        # Fall back to character splitting for 9-char contiguous strings.
        elif len(normalized.strip()) == 9:
            tokens = list(normalized.strip())
        else:
            tokens = normalized.split()

        # Convert tokens to integers.
        try:
            return [int(t) for t in tokens]
        except ValueError:
            self.raise_error(
                'INVALID_STATE',
                f'Cannot parse state: {state_str}',
                state=state_str,
            )

    # * method: verify_state
    def verify_state(self, state: List[int]) -> None:
        '''
        Verify that a puzzle state is valid: exactly 9 tiles with values 0-8, each appearing once.

        :param state: The puzzle state to verify.
        :type state: List[int]
        '''

        # Verify exactly 9 tiles with values 0-8, each appearing once.
        self.verify(
            expression=sorted(state) == list(range(9)),
            error_code='INVALID_STATE',
            message=f'State must contain exactly 9 tiles with values 0-8: {state}',
            state=str(state),
        )

    # * method: is_solvable
    def is_solvable(self, state: List[int], goal: List[int]) -> bool:
        '''
        Check whether a puzzle state is solvable relative to a goal state
        by comparing inversion parities.

        :param state: The start state.
        :type state: List[int]
        :param goal: The goal state.
        :type goal: List[int]
        :return: True if the state is solvable relative to the goal.
        :rtype: bool
        '''

        # Count inversions for a given state (ignoring blank tile 0).
        def count_inversions(s: List[int]) -> int:
            inv = 0
            tiles = [t for t in s if t != 0]
            for i in range(len(tiles)):
                for j in range(i + 1, len(tiles)):
                    if tiles[i] > tiles[j]:
                        inv += 1
            return inv

        # Return True if both states have the same inversion parity.
        return count_inversions(state) % 2 == count_inversions(goal) % 2

    # * method: format_grid
    def format_grid(self, state: List[int], blank_symbol: str = '*') -> str:
        '''
        Format a flat puzzle state as a 3x3 grid string.

        :param state: The puzzle state as a flat list of 9 integers.
        :type state: List[int]
        :param blank_symbol: The symbol to use for the blank tile (0).
        :type blank_symbol: str
        :return: A newline-joined string of 3 rows.
        :rtype: str
        '''

        # Replace 0 with the blank symbol and format as 3 rows.
        display = [blank_symbol if t == 0 else str(t) for t in state]
        rows = [
            ' '.join(display[i:i + 3])
            for i in range(0, 9, 3)
        ]

        # Return the newline-joined grid.
        return '\n'.join(rows)
