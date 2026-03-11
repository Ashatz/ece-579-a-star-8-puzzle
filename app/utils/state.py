# *** imports

# ** core
import re
from typing import List

# ** infra
from tiferet.events import RaiseError


# *** utils

# ** util: puzzle_state_parser
class PuzzleStateParser:
    '''
    Utility for parsing, validating, and formatting 8-puzzle states.
    Provides static methods for converting user-facing state strings
    into internal integer lists, verifying state validity, checking
    solvability via inversion parity, and pretty-printing grids.
    '''

    # * method: parse_state (static)
    @staticmethod
    def parse_state(state_str: str) -> List[int]:
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
            RaiseError.execute(
                error_code='INVALID_STATE',
                message=f'Could not parse state: {state_str}',
                state=state_str,
            )

        # Return the parsed state.
        return state

    # * method: verify_state (static)
    @staticmethod
    def verify_state(state: List[int]) -> None:
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
        if not is_valid:
            RaiseError.execute(
                error_code='INVALID_STATE',
                message=f'Invalid state: {state}. Must contain exactly 9 tiles (0-8, each once).',
                state=str(state),
            )

    # * method: is_solvable (static)
    @staticmethod
    def is_solvable(state: List[int], goal: List[int]) -> bool:
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

    # * method: format_grid (static)
    @staticmethod
    def format_grid(state: List[int], blank_symbol: str = '*') -> str:
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
