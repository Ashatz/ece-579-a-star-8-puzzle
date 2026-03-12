# *** imports

# ** core
import time
from typing import Any, Dict

# ** app
from .settings import DomainEvent
from ..utils import State, Heuristic, AStar


# *** events

# ** event: solve_puzzle
class SolvePuzzle(DomainEvent):
    '''
    A domain event to solve the 8-puzzle using the A* search algorithm.
    Supports misplaced, manhattan, linear-conflict, and pattern-db heuristics.
    Delegates state parsing, validation, search, and heuristic computation
    to utility classes in app.utils.
    '''

    # * method: execute
    def execute(self,
            start: str,
            goal: str = '1,2,3,4,5,6,7,8,*',
            heuristic: str = 'manhattan',
            blank_symbol: str = '*',
            **kwargs,
        ) -> str:
        '''
        Execute the A* search to solve the 8-puzzle.

        :param start: The initial state as a string.
        :type start: str
        :param goal: The goal state as a string.
        :type goal: str
        :param heuristic: The heuristic to use ('misplaced', 'manhattan', 'linear-conflict', or 'pattern-db').
        :type heuristic: str
        :param blank_symbol: The symbol to display for the blank tile.
        :type blank_symbol: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A formatted string containing the solution path and metrics.
        :rtype: str
        '''

        # Validate the heuristic selection.
        valid_heuristics = ('misplaced', 'manhattan', 'linear-conflict', 'pattern-db')
        self.verify(
            heuristic in valid_heuristics,
            'INVALID_HEURISTIC',
            f'Unsupported heuristic: {heuristic}',
            heuristic=heuristic,
        )

        # Parse and validate the start state.
        start_state = State.parse_state(start)
        State.verify_state(start_state)

        # Parse and validate the goal state.
        goal_state = State.parse_state(goal)
        State.verify_state(goal_state)

        # Check if the puzzle is solvable.
        self.verify(
            State.is_solvable(start_state, goal_state),
            'UNSOLVABLE_STATE',
            'This configuration is unsolvable (mismatched inversion parity).',
            start=start,
            goal=goal,
        )

        # Select the heuristic function.
        heuristic_map = {
            'misplaced': Heuristic.misplaced,
            'manhattan': Heuristic.manhattan,
            'linear-conflict': Heuristic.linear_conflict,
            'pattern-db': Heuristic.pattern_db,
        }
        heuristic_fn = heuristic_map[heuristic]

        # Run A* search.
        start_time = time.perf_counter()
        path, nodes_expanded = AStar.search(start_state, goal_state, heuristic_fn)
        elapsed = time.perf_counter() - start_time

        # Format the solution steps as grids.
        formatted_steps = []
        for i, state in enumerate(path):
            header = f'Step {i}:'
            grid = State.format_grid(state, blank_symbol)
            formatted_steps.append(f'{header}\n{grid}')

        # Build the output string.
        output_lines = [
            f'Heuristic: {heuristic}',
            f'Moves: {len(path) - 1}',
            f'Nodes expanded: {nodes_expanded}',
            f'Time: {elapsed:.4f}s',
            '',
        ]
        output_lines.extend(formatted_steps)

        # Return the result as a formatted string.
        return '\n'.join(output_lines)
