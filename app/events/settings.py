# *** imports

# ** core
import re
from collections import deque
from typing import Dict, List, Tuple

# ** infra
from tiferet.events import *


# *** constants

# ** constant: adjacency_3x3
ADJACENCY_3X3 = {
    0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
    3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
    6: [3, 7], 7: [4, 6, 8], 8: [5, 7],
}

# ** constant: pdb_tiles
_PDB_TILES_1 = [1, 2, 3, 4]
_PDB_TILES_2 = [5, 6, 7, 8]


# *** classes

# ** class: pdb_cache
_PDB_CACHE: Dict[Tuple[int, ...], Tuple[dict, dict]] = {}


def _abstract_state(state, sorted_tiles: List[int]) -> Tuple[int, ...]:
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


def _precompute_pdb(tiles: set, goal: Tuple[int, ...]) -> Dict[Tuple[int, ...], int]:
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
    goal_abstract = _abstract_state(goal, sorted_tiles)

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


def _get_pdb_tables(goal: Tuple[int, ...]) -> Tuple[dict, dict]:
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
    pdb1 = _precompute_pdb({1, 2, 3, 4}, goal)
    pdb2 = _precompute_pdb({5, 6, 7, 8}, goal)

    # Cache and return.
    _PDB_CACHE[goal] = (pdb1, pdb2)
    return pdb1, pdb2


def pattern_db_lookup(state, goal) -> int:
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
    pdb1, pdb2 = _get_pdb_tables(goal_tuple)

    # Look up abstract states for each pattern.
    abs1 = _abstract_state(state, _PDB_TILES_1)
    abs2 = _abstract_state(state, _PDB_TILES_2)

    # Sum the costs (0 fallback if abstract state not found).
    h1 = pdb1.get(abs1, 0)
    h2 = pdb2.get(abs2, 0)

    # Return the additive heuristic value.
    return h1 + h2


# *** events

# ** event: puzzle_event
class PuzzleEvent(DomainEvent):
    '''
    A base domain event for 8-puzzle operations.
    Provides shared utilities for state parsing, validation,
    solvability checking, and grid formatting.
    '''

    # * method: parse_state
    def parse_state(self, state_str: str) -> List[int]:
        '''
        Parse a user-provided state string into an internal list of integers.
        Accepts comma-separated, space-separated, or contiguous formats.
        The blank tile can be represented as '*' or '0'.

        :param state_str: The state string to parse.
        :type state_str: str
        :return: A list of 9 integers representing the puzzle state.
        :rtype: List[int]
        '''

        # Normalize the blank symbol to '0'.
        normalized = state_str.replace('*', '0')

        # Split on commas or whitespace.
        tokens = re.split(r'[,\s]+', normalized.strip())

        # If splitting produced a single token, split by character (e.g. "123405678").
        if len(tokens) == 1 and len(tokens[0]) == 9:
            tokens = list(tokens[0])

        # Convert tokens to integers.
        try:
            state = [int(t) for t in tokens]
        except ValueError:
            self.raise_error(
                'INVALID_STATE',
                f'Could not parse state: {state_str}',
                state=state_str,
            )

        # Return the parsed state.
        return state

    # * method: verify_state
    def verify_state(self, state: List[int]) -> None:
        '''
        Verify that a puzzle state is valid: exactly 9 tiles, values 0-8,
        each appearing exactly once.

        :param state: The puzzle state to verify.
        :type state: List[int]
        '''

        # Verify the state has exactly 9 tiles with values 0-8.
        is_valid = (
            len(state) == 9
            and sorted(state) == list(range(9))
        )

        # Raise an error if the state is invalid.
        self.verify(
            is_valid,
            'INVALID_STATE',
            f'Invalid state: {state}. Must contain exactly 9 tiles (0-8, each once).',
            state=str(state),
        )

    # * method: is_solvable
    def is_solvable(self, state: List[int], goal: List[int]) -> bool:
        '''
        Check whether the puzzle is solvable by comparing inversion parities.
        For a 3x3 puzzle, a state is reachable from the goal if and only if
        both have the same inversion parity (both even or both odd).

        :param state: The initial puzzle state.
        :type state: List[int]
        :param goal: The goal puzzle state.
        :type goal: List[int]
        :return: True if the puzzle is solvable, False otherwise.
        :rtype: bool
        '''

        # Count inversions for a given state (ignoring the blank tile).
        def count_inversions(s: List[int]) -> int:
            tiles = [t for t in s if t != 0]
            inversions = 0
            for i in range(len(tiles)):
                for j in range(i + 1, len(tiles)):
                    if tiles[i] > tiles[j]:
                        inversions += 1
            return inversions

        # Compare parities of both states.
        return count_inversions(state) % 2 == count_inversions(goal) % 2

    # * method: format_grid
    def format_grid(self, state: List[int], blank_symbol: str = '*') -> str:
        '''
        Format a puzzle state as a pretty-printed 3x3 grid.

        :param state: The puzzle state to format.
        :type state: List[int]
        :param blank_symbol: The symbol to display for the blank tile.
        :type blank_symbol: str
        :return: The formatted grid string.
        :rtype: str
        '''

        # Replace 0 with the blank symbol and format as rows.
        symbols = [blank_symbol if t == 0 else str(t) for t in state]
        rows = [
            ' '.join(symbols[i:i + 3])
            for i in range(0, 9, 3)
        ]

        # Return the grid as a newline-separated string.
        return '\n'.join(rows)
