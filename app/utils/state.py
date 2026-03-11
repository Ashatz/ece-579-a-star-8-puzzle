# *** imports

# ** core
from typing import List

# ** infra
from tiferet.events import RaiseError


# *** utils

# ** util: puzzle_state_parser
class PuzzleStateParser:
    '''
    Utility for parsing, validating, and formatting 8-puzzle states.
    Decouples state-handling logic from the domain event layer.
    '''

    # * method: parse_state (static)
    @staticmethod
    def parse_state(state_str: str) -> List[int]:
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
            RaiseError.execute(
                error_code='INVALID_STATE',
                state=state_str,
            )

    # * method: verify_state (static)
    @staticmethod
    def verify_state(state: List[int]) -> None:
        '''
        Verify that a puzzle state is valid: exactly 9 tiles with values 0-8,
        each appearing once.

        :param state: The puzzle state to verify.
        :type state: List[int]
        '''

        # Verify exactly 9 tiles with values 0-8, each appearing once.
        if sorted(state) != list(range(9)):
            RaiseError.execute(
                error_code='INVALID_STATE',
                state=str(state),
            )

    # * method: is_solvable (static)
    @staticmethod
    def is_solvable(state: List[int], goal: List[int]) -> bool:
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

    # * method: format_grid (static)
    @staticmethod
    def format_grid(state: List[int], blank_symbol: str = '*') -> str:
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
