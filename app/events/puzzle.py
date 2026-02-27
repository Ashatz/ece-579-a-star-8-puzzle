# *** imports

# ** core
import heapq
import time
from typing import Any, Dict, List, Tuple

# ** app
from .settings import PuzzleEvent, pattern_db_lookup


# *** events

# ** event: solve_puzzle
class SolvePuzzle(PuzzleEvent):
    '''
    A domain event to solve the 8-puzzle using the A* search algorithm.
    Supports misplaced, manhattan, linear-conflict, and pattern-db heuristics.
    '''

    # * method: execute
    def execute(self,
            start: str,
            goal: str = '1,2,3,4,5,6,7,8,*',
            heuristic: str = 'manhattan',
            blank_symbol: str = '*',
            **kwargs,
        ) -> Dict[str, Any]:
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
        :return: A dictionary containing the solution path and metrics.
        :rtype: Dict[str, Any]
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
        start_state = self.parse_state(start)
        self.verify_state(start_state)

        # Parse and validate the goal state.
        goal_state = self.parse_state(goal)
        self.verify_state(goal_state)

        # Check if the puzzle is solvable.
        self.verify(
            self.is_solvable(start_state, goal_state),
            'UNSOLVABLE_STATE',
            'This configuration is unsolvable (mismatched inversion parity).',
            start=start,
            goal=goal,
        )

        # Select the heuristic function.
        heuristic_map = {
            'misplaced': self._misplaced,
            'manhattan': self._manhattan,
            'linear-conflict': self._linear_conflict,
            'pattern-db': self._pattern_db,
        }
        heuristic_fn = heuristic_map[heuristic]

        # Run A* search.
        start_time = time.perf_counter()
        path, nodes_expanded = self._astar(start_state, goal_state, heuristic_fn)
        elapsed = time.perf_counter() - start_time

        # Format the solution steps as grids.
        formatted_steps = []
        for i, state in enumerate(path):
            header = f'Step {i}:'
            grid = self.format_grid(state, blank_symbol)
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

    # * method: _astar
    def _astar(self,
            start: List[int],
            goal: List[int],
            heuristic_fn,
        ) -> Tuple[List[List[int]], int]:
        '''
        Run the A* search algorithm.

        :param start: The initial state.
        :type start: List[int]
        :param goal: The goal state.
        :type goal: List[int]
        :param heuristic_fn: The heuristic function to use.
        :type heuristic_fn: callable
        :return: A tuple of (solution path, nodes expanded).
        :rtype: Tuple[List[List[int]], int]
        '''

        # Convert states to tuples for hashing.
        start_tuple = tuple(start)
        goal_tuple = tuple(goal)

        # Initialize the open set as a priority queue: (f, tie-breaker, state).
        counter = 0
        open_set = [(heuristic_fn(start, goal), counter, start_tuple)]
        heapq.heapify(open_set)

        # Track the best g-score for each state.
        g_scores = {start_tuple: 0}

        # Track parent states for path reconstruction.
        parents = {start_tuple: None}

        # Track visited states.
        closed_set = set()

        # Count nodes expanded.
        nodes_expanded = 0

        # A* main loop.
        while open_set:

            # Pop the state with the lowest f-score.
            f, _, current = heapq.heappop(open_set)

            # Skip if already visited.
            if current in closed_set:
                continue

            # Mark the current state as visited.
            closed_set.add(current)
            nodes_expanded += 1

            # Check if we reached the goal.
            if current == goal_tuple:
                path = self._reconstruct_path(parents, current)
                return path, nodes_expanded

            # Get the current g-score.
            current_g = g_scores[current]

            # Generate neighbors by swapping the blank with adjacent tiles.
            for neighbor in self._get_neighbors(current):

                # Skip already visited neighbors.
                if neighbor in closed_set:
                    continue

                # Calculate the tentative g-score.
                tentative_g = current_g + 1

                # Update if this path is better.
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    h = heuristic_fn(list(neighbor), goal)
                    f = tentative_g + h
                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))
                    parents[neighbor] = current

        # Should not reach here if solvability was checked.
        return [start], nodes_expanded

    # * method: _get_neighbors
    def _get_neighbors(self, state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        '''
        Generate all valid neighbor states by swapping the blank tile
        with an adjacent tile.

        :param state: The current state as a tuple.
        :type state: Tuple[int, ...]
        :return: A list of neighbor states.
        :rtype: List[Tuple[int, ...]]
        '''

        # Find the position of the blank tile.
        blank_idx = state.index(0)
        row, col = blank_idx // 3, blank_idx % 3

        # Define possible moves (up, down, left, right).
        moves = []
        if row > 0:
            moves.append(blank_idx - 3)  # up
        if row < 2:
            moves.append(blank_idx + 3)  # down
        if col > 0:
            moves.append(blank_idx - 1)  # left
        if col < 2:
            moves.append(blank_idx + 1)  # right

        # Generate neighbor states.
        neighbors = []
        for swap_idx in moves:
            new_state = list(state)
            new_state[blank_idx], new_state[swap_idx] = new_state[swap_idx], new_state[blank_idx]
            neighbors.append(tuple(new_state))

        # Return the list of neighbors.
        return neighbors

    # * method: _reconstruct_path
    def _reconstruct_path(self,
            parents: Dict[Tuple[int, ...], Tuple[int, ...] | None],
            current: Tuple[int, ...],
        ) -> List[List[int]]:
        '''
        Reconstruct the solution path from start to goal.

        :param parents: The parent map.
        :type parents: Dict[Tuple[int, ...], Tuple[int, ...] | None]
        :param current: The goal state.
        :type current: Tuple[int, ...]
        :return: The solution path as a list of states.
        :rtype: List[List[int]]
        '''

        # Build the path by tracing parents from goal to start.
        path = []
        while current is not None:
            path.append(list(current))
            current = parents[current]

        # Reverse to get start-to-goal order.
        path.reverse()

        # Return the path.
        return path

    # * method: _linear_conflict
    def _linear_conflict(self, state: List[int], goal: List[int]) -> int:
        '''
        Calculate Manhattan distance plus linear conflict penalty.
        Adds +2 for each pair of tiles in the same row or column that
        are in their correct line but reversed relative to their goal
        positions.

        :param state: The current state.
        :type state: List[int]
        :param goal: The goal state.
        :type goal: List[int]
        :return: Manhattan distance plus linear conflict penalty.
        :rtype: int
        '''

        # Start with the Manhattan distance.
        manhattan = self._manhattan(state, goal)

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

    # * method: _pattern_db
    def _pattern_db(self, state: List[int], goal: List[int]) -> int:
        '''
        Look up the additive pattern database heuristic value.
        Uses two disjoint 4-tile patterns ({1,2,3,4} and {5,6,7,8})
        precomputed via BFS.

        :param state: The current state.
        :type state: List[int]
        :param goal: The goal state.
        :type goal: List[int]
        :return: The sum of PDB lookups for both patterns.
        :rtype: int
        '''

        # Delegate to the module-level PDB lookup.
        return pattern_db_lookup(state, goal)

    # * method: _misplaced
    def _misplaced(self, state: List[int], goal: List[int]) -> int:
        '''
        Count the number of misplaced tiles (excluding the blank).

        :param state: The current state.
        :type state: List[int]
        :param goal: The goal state.
        :type goal: List[int]
        :return: The number of misplaced tiles.
        :rtype: int
        '''

        # Count tiles that are not in their goal position (excluding blank).
        return sum(
            1 for i in range(9)
            if state[i] != 0 and state[i] != goal[i]
        )

    # * method: _manhattan
    def _manhattan(self, state: List[int], goal: List[int]) -> int:
        '''
        Calculate the sum of Manhattan distances for all tiles
        (excluding the blank) from their current position to their
        goal position.

        :param state: The current state.
        :type state: List[int]
        :param goal: The goal state.
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
