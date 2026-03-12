# *** imports

# ** core
from typing import List

# ** app
from .pdb import PatternDatabase


# *** utils

# ** util: heuristic_calculator
class HeuristicCalculator:
    '''
    Utility for computing admissible heuristic values for the 8-puzzle.
    Provides static methods for four heuristics: misplaced tiles,
    Manhattan distance, linear conflict (Manhattan + reversed-pair
    penalty), and additive pattern database lookup. All methods accept
    (state, goal) as flat integer lists and return an integer cost
    estimate.
    '''

    # * method: misplaced (static)
    @staticmethod
    def misplaced(state: List[int], goal: List[int]) -> int:
        '''
        Count the number of misplaced tiles (excluding the blank).

        :param state: The current state as a flat list of 9 ints.
        :type state: List[int]
        :param goal: The goal state as a flat list of 9 ints.
        :type goal: List[int]
        :return: The number of misplaced tiles.
        :rtype: int
        '''

        # Count tiles that are not in their goal position (excluding blank).
        return sum(
            1 for i in range(9)
            if state[i] != 0 and state[i] != goal[i]
        )

    # * method: manhattan (static)
    @staticmethod
    def manhattan(state: List[int], goal: List[int]) -> int:
        '''
        Calculate the sum of Manhattan distances for all tiles
        (excluding the blank) from their current position to their
        goal position.

        :param state: The current state as a flat list of 9 ints.
        :type state: List[int]
        :param goal: The goal state as a flat list of 9 ints.
        :type goal: List[int]
        :return: The total Manhattan distance.
        :rtype: int
        '''

        # Build a lookup from tile value to goal index.
        goal_index = {goal[i]: i for i in range(9)}

        # Sum the Manhattan distances for each non-blank tile.
        distance = 0
        for i in range(9):
            tile = state[i]
            if tile == 0:
                continue
            goal_pos = goal_index[tile]
            current_row, current_col = i // 3, i % 3
            goal_row, goal_col = goal_pos // 3, goal_pos % 3
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)

        # Return the total distance.
        return distance

    # * method: linear_conflict (static)
    @staticmethod
    def linear_conflict(state: List[int], goal: List[int]) -> int:
        '''
        Calculate Manhattan distance plus linear conflict penalty.
        Adds +2 for each pair of tiles in the same row or column that
        are in their correct line but reversed relative to their goal
        positions.

        :param state: The current state as a flat list of 9 ints.
        :type state: List[int]
        :param goal: The goal state as a flat list of 9 ints.
        :type goal: List[int]
        :return: Manhattan distance plus linear conflict penalty.
        :rtype: int
        '''

        # Start with the Manhattan distance.
        manhattan = HeuristicCalculator.manhattan(state, goal)

        # Build a lookup from tile value to goal index.
        goal_index = {goal[i]: i for i in range(9)}

        # Count linear conflicts.
        conflict = 0

        # Check rows for conflicts.
        for row in range(3):
            tiles_in_row = []
            for col in range(3):
                tile = state[row * 3 + col]
                if tile != 0:
                    g_pos = goal_index[tile]
                    g_row = g_pos // 3
                    g_col = g_pos % 3
                    if g_row == row:
                        tiles_in_row.append((col, g_col))

            # Detect reversed pairs (current col order vs goal col order).
            for i in range(len(tiles_in_row)):
                for j in range(i + 1, len(tiles_in_row)):
                    _, goal_col_i = tiles_in_row[i]
                    _, goal_col_j = tiles_in_row[j]
                    if goal_col_i > goal_col_j:
                        conflict += 2

        # Check columns for conflicts.
        for col in range(3):
            tiles_in_col = []
            for row in range(3):
                tile = state[row * 3 + col]
                if tile != 0:
                    g_pos = goal_index[tile]
                    g_row = g_pos // 3
                    g_col = g_pos % 3
                    if g_col == col:
                        tiles_in_col.append((row, g_row))

            # Detect reversed pairs (current row order vs goal row order).
            for i in range(len(tiles_in_col)):
                for j in range(i + 1, len(tiles_in_col)):
                    _, goal_row_i = tiles_in_col[i]
                    _, goal_row_j = tiles_in_col[j]
                    if goal_row_i > goal_row_j:
                        conflict += 2

        # Return Manhattan plus conflict penalty.
        return manhattan + conflict

    # * method: pattern_db (static)
    @staticmethod
    def pattern_db(state: List[int], goal: List[int]) -> int:
        '''
        Look up the additive pattern database heuristic value.
        Delegates to PatternDatabase.lookup() which uses two disjoint
        4-tile patterns ({1,2,3,4} and {5,6,7,8}) precomputed via BFS.

        :param state: The current state as a flat list of 9 ints.
        :type state: List[int]
        :param goal: The goal state as a flat list of 9 ints.
        :type goal: List[int]
        :return: The sum of PDB lookups for both patterns.
        :rtype: int
        '''

        # Delegate to the PatternDatabase utility.
        return PatternDatabase.lookup(state, goal)
