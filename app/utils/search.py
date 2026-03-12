# *** imports

# ** core
import heapq
from typing import Callable, Dict, List, Tuple


# *** constants

# ** constant: adjacency_3x3
ADJACENCY_3X3 = {
    0: [1, 3], 1: [0, 2, 4], 2: [1, 5],
    3: [0, 4, 6], 4: [1, 3, 5, 7], 5: [2, 4, 8],
    6: [3, 7], 7: [4, 6, 8], 8: [5, 7],
}


# *** utils

# ** util: a_star_search
class AStarSearch:
    '''
    Utility for solving the 8-puzzle via the A* search algorithm.
    Provides static methods for running A* search, generating
    neighbor states by blank-tile swaps on a 3x3 grid, and
    reconstructing the solution path from a parent map.
    '''

    # * method: search (static)
    @staticmethod
    def search(
            start: List[int],
            goal: List[int],
            heuristic_fn: Callable[[List[int], List[int]], int],
        ) -> Tuple[List[List[int]], int]:
        '''
        Run the A* search algorithm on the 8-puzzle.

        :param start: The initial state as a flat list of 9 ints.
        :type start: List[int]
        :param goal: The goal state as a flat list of 9 ints.
        :type goal: List[int]
        :param heuristic_fn: A heuristic function accepting (state, goal) and returning an int.
        :type heuristic_fn: Callable[[List[int], List[int]], int]
        :return: A tuple of (solution path as list of states, nodes expanded).
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
                path = AStarSearch.reconstruct_path(parents, current)
                return path, nodes_expanded

            # Get the current g-score.
            current_g = g_scores[current]

            # Generate neighbors by swapping the blank with adjacent tiles.
            for neighbor in AStarSearch.get_neighbors(current):

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

    # * method: get_neighbors (static)
    @staticmethod
    def get_neighbors(state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
        '''
        Generate all valid neighbor states by swapping the blank tile
        with an adjacent tile on the 3x3 grid.

        :param state: The current state as a tuple of 9 ints.
        :type state: Tuple[int, ...]
        :return: A list of neighbor states.
        :rtype: List[Tuple[int, ...]]
        '''

        # Find the position of the blank tile.
        blank_idx = state.index(0)

        # Generate neighbor states using the adjacency map.
        neighbors = []
        for swap_idx in ADJACENCY_3X3[blank_idx]:
            new_state = list(state)
            new_state[blank_idx], new_state[swap_idx] = new_state[swap_idx], new_state[blank_idx]
            neighbors.append(tuple(new_state))

        # Return the list of neighbors.
        return neighbors

    # * method: reconstruct_path (static)
    @staticmethod
    def reconstruct_path(
            parents: Dict[Tuple[int, ...], Tuple[int, ...] | None],
            current: Tuple[int, ...],
        ) -> List[List[int]]:
        '''
        Reconstruct the solution path from start to goal by tracing
        the parent map backward from the goal state.

        :param parents: A mapping from each state to its predecessor.
        :type parents: Dict[Tuple[int, ...], Tuple[int, ...] | None]
        :param current: The goal state to trace back from.
        :type current: Tuple[int, ...]
        :return: The solution path as a list of states (start to goal).
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
