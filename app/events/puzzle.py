# *** imports

# ** core
import heapq
import time
from typing import Any, Dict, List, Tuple

# ** app
from .settings import PuzzleEvent


# *** events

# ** event: solve_puzzle
class SolvePuzzle(PuzzleEvent):
    '''
    Domain event to solve an 8-puzzle using A* search
    with a configurable heuristic function.
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
        Solve the 8-puzzle from a start state to a goal state using A* search.

        :param start: The start state as a string.
        :type start: str
        :param goal: The goal state as a string.
        :type goal: str
        :param heuristic: The heuristic to use ('misplaced' or 'manhattan').
        :type heuristic: str
        :param blank_symbol: The symbol to display for the blank tile.
        :type blank_symbol: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A formatted string with the solution details.
        :rtype: str
        '''

        # Validate the heuristic name.
        valid_heuristics = ('misplaced', 'manhattan')
        self.verify(
            expression=heuristic in valid_heuristics,
            error_code='INVALID_HEURISTIC',
            message=f'Invalid heuristic: {heuristic}. Must be one of {valid_heuristics}.',
            heuristic=heuristic,
        )

        # Parse and validate the start state.
        start_state = self.parse_state(str(start))
        self.verify_state(start_state)

        # Parse and validate the goal state.
        goal_state = self.parse_state(str(goal))
        self.verify_state(goal_state)

        # Check solvability.
        self.verify(
            expression=self.is_solvable(start_state, goal_state),
            error_code='UNSOLVABLE_STATE',
            message='The given start state is not solvable for the given goal state.',
            start=str(start_state),
            goal=str(goal_state),
        )

        # Select the heuristic function.
        heuristic_map: Dict[str, Any] = {
            'misplaced': self._misplaced,
            'manhattan': self._manhattan,
        }
        heuristic_fn = heuristic_map[heuristic]

        # Run A* search and time execution.
        t0 = time.perf_counter()
        path, nodes_expanded = self._astar(start_state, goal_state, heuristic_fn)
        elapsed = time.perf_counter() - t0

        # Format the solution output.
        lines = [
            f'Heuristic: {heuristic}',
            f'Moves:     {len(path) - 1}',
            f'Nodes:     {nodes_expanded}',
            f'Time:      {elapsed:.4f}s',
            '',
        ]
        for i, step in enumerate(path):
            lines.append(f'Step {i}:')
            lines.append(self.format_grid(step, blank_symbol))
            lines.append('')

        # Return the formatted solution string.
        return '\n'.join(lines)

    # * method: _astar
    def _astar(self,
            start: List[int],
            goal: List[int],
            heuristic_fn,
        ) -> Tuple[List[List[int]], int]:
        '''
        Perform A* search from start to goal using the given heuristic.

        :param start: The start state as a flat list.
        :type start: List[int]
        :param goal: The goal state as a flat list.
        :type goal: List[int]
        :param heuristic_fn: A callable that computes h(state, goal).
        :type heuristic_fn: callable
        :return: A tuple of (path as list of states, nodes expanded count).
        :rtype: Tuple[List[List[int]], int]
        '''

        # Initialize the A* data structures.
        start_tuple = tuple(start)
        goal_tuple = tuple(goal)
        h = heuristic_fn(start_tuple, goal_tuple)
        counter = 0
        open_set = [(h, counter, start_tuple)]
        g_score = {start_tuple: 0}
        parents: Dict[Tuple[int, ...], Tuple[int, ...] | None] = {start_tuple: None}
        closed_set = set()
        nodes_expanded = 0

        # Run the A* search loop.
        while open_set:

            # Pop the node with the lowest f-score.
            f, _, current = heapq.heappop(open_set)

            # Skip if already visited.
            if current in closed_set:
                continue

            # Mark as visited.
            closed_set.add(current)
            nodes_expanded += 1

            # Check if the goal has been reached.
            if current == goal_tuple:
                path = self._reconstruct_path(parents, current)
                return path, nodes_expanded

            # Expand neighbors.
            for neighbor in self._get_neighbors(current):
                if neighbor in closed_set:
                    continue

                # Calculate the tentative g-score.
                tentative_g = g_score[current] + 1

                # Update if this path is better.
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic_fn(neighbor, goal_tuple)
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    parents[neighbor] = current

        # Should not reach here for solvable puzzles.
        return [], nodes_expanded

    # * method: _get_neighbors
    def _get_neighbors(self, state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        '''
        Generate all valid neighbor states by swapping the blank tile
        with adjacent tiles.

        :param state: The current state as a tuple.
        :type state: Tuple[int, ...]
        :return: A list of neighbor states.
        :rtype: List[Tuple[int, ...]]
        '''

        # Find the blank (0) position.
        blank = state.index(0)
        row, col = divmod(blank, 3)
        neighbors = []

        # Generate moves: up, down, left, right.
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                ni = nr * 3 + nc
                s = list(state)
                s[blank], s[ni] = s[ni], s[blank]
                neighbors.append(tuple(s))

        # Return the list of neighbor states.
        return neighbors

    # * method: _reconstruct_path
    def _reconstruct_path(self,
            parents: Dict[Tuple[int, ...], Tuple[int, ...] | None],
            current: Tuple[int, ...],
        ) -> List[List[int]]:
        '''
        Reconstruct the path from start to goal by tracing the parent chain.

        :param parents: A mapping from state to its parent state.
        :type parents: Dict[Tuple[int, ...], Tuple[int, ...] | None]
        :param current: The goal state.
        :type current: Tuple[int, ...]
        :return: The path from start to goal as a list of states.
        :rtype: List[List[int]]
        '''

        # Trace the parent chain from goal to start.
        path = []
        while current is not None:
            path.append(list(current))
            current = parents[current]

        # Reverse to get start-to-goal order.
        path.reverse()

        # Return the path.
        return path

    # * method: _misplaced
    def _misplaced(self,
            state: Tuple[int, ...],
            goal: Tuple[int, ...],
        ) -> int:
        '''
        Count the number of non-blank tiles not in their goal position.

        :param state: The current state.
        :type state: Tuple[int, ...]
        :param goal: The goal state.
        :type goal: Tuple[int, ...]
        :return: The number of misplaced tiles.
        :rtype: int
        '''

        # Count non-blank tiles not in their goal position.
        return sum(
            1 for s, g in zip(state, goal)
            if s != 0 and s != g
        )

    # * method: _manhattan
    def _manhattan(self,
            state: Tuple[int, ...],
            goal: Tuple[int, ...],
        ) -> int:
        '''
        Compute the Manhattan distance heuristic for all non-blank tiles.

        :param state: The current state.
        :type state: Tuple[int, ...]
        :param goal: The goal state.
        :type goal: Tuple[int, ...]
        :return: The sum of Manhattan distances.
        :rtype: int
        '''

        # Build a mapping of tile value to goal position.
        goal_positions = {val: idx for idx, val in enumerate(goal)}
        total = 0

        # Sum |row_diff| + |col_diff| for each non-blank tile.
        for idx, val in enumerate(state):
            if val != 0:
                goal_idx = goal_positions[val]
                r1, c1 = divmod(idx, 3)
                r2, c2 = divmod(goal_idx, 3)
                total += abs(r1 - r2) + abs(c1 - c2)

        # Return the total Manhattan distance.
        return total
