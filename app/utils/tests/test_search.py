# *** imports

# ** infra
import pytest

# ** app
from app.utils.search import AStarSearch, ADJACENCY_3X3


# *** constants

# ** constant: goal_state
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]


# *** helpers

# ** helper: misplaced_heuristic
def misplaced_heuristic(state, goal):
    '''
    Trivial misplaced-tiles heuristic for testing search.
    '''
    return sum(
        1 for i in range(9)
        if state[i] != 0 and state[i] != goal[i]
    )


# *** tests

# ** test: get_neighbors_center
def test_get_neighbors_center() -> None:
    '''
    Test neighbor generation with the blank at center position (4).
    The center has 4 adjacent positions: 1, 3, 5, 7.
    '''

    # Create a state with blank at center (position 4).
    state = (1, 2, 3, 4, 0, 6, 7, 8, 5)

    # Generate neighbors.
    neighbors = AStarSearch.get_neighbors(state)

    # Assert 4 neighbors are generated (up, down, left, right).
    assert len(neighbors) == 4

    # Assert each neighbor has the blank swapped to an adjacent position.
    blank_positions = {n.index(0) for n in neighbors}
    assert blank_positions == {1, 3, 5, 7}


# ** test: get_neighbors_corner
def test_get_neighbors_corner() -> None:
    '''
    Test neighbor generation with the blank at corner position (0).
    The top-left corner has 2 adjacent positions: 1, 3.
    '''

    # Create a state with blank at top-left corner (position 0).
    state = (0, 2, 3, 1, 5, 6, 4, 7, 8)

    # Generate neighbors.
    neighbors = AStarSearch.get_neighbors(state)

    # Assert 2 neighbors are generated (right and down).
    assert len(neighbors) == 2

    # Assert the blank moved to positions 1 and 3.
    blank_positions = {n.index(0) for n in neighbors}
    assert blank_positions == {1, 3}


# ** test: get_neighbors_edge
def test_get_neighbors_edge() -> None:
    '''
    Test neighbor generation with the blank at an edge position (1).
    The top-center has 3 adjacent positions: 0, 2, 4.
    '''

    # Create a state with blank at top-center (position 1).
    state = (2, 0, 3, 1, 5, 6, 4, 7, 8)

    # Generate neighbors.
    neighbors = AStarSearch.get_neighbors(state)

    # Assert 3 neighbors are generated.
    assert len(neighbors) == 3

    # Assert the blank moved to positions 0, 2, and 4.
    blank_positions = {n.index(0) for n in neighbors}
    assert blank_positions == {0, 2, 4}


# ** test: reconstruct_path
def test_reconstruct_path() -> None:
    '''
    Test path reconstruction from a simple 3-step parent map.
    '''

    # Build a parent map: A -> B -> C (start -> mid -> goal).
    state_a = (1, 2, 3, 4, 5, 6, 7, 0, 8)
    state_b = (1, 2, 3, 4, 5, 6, 0, 7, 8)
    state_c = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    parents = {state_a: None, state_b: state_a, state_c: state_b}

    # Reconstruct the path from the goal.
    path = AStarSearch.reconstruct_path(parents, state_c)

    # Assert the path is in start-to-goal order.
    assert len(path) == 3
    assert path[0] == list(state_a)
    assert path[1] == list(state_b)
    assert path[2] == list(state_c)


# ** test: search_already_solved
def test_search_already_solved() -> None:
    '''
    Test A* search when start equals goal (zero moves).
    '''

    # Run search with start == goal.
    path, nodes_expanded = AStarSearch.search(
        GOAL_STATE,
        GOAL_STATE,
        misplaced_heuristic,
    )

    # Assert the path contains only the goal state.
    assert len(path) == 1
    assert path[0] == GOAL_STATE

    # Assert only one node was expanded (the start/goal).
    assert nodes_expanded == 1


# ** test: search_one_move
def test_search_one_move() -> None:
    '''
    Test A* search for a puzzle one move from the goal.
    '''

    # Start: blank at position 7, tile 8 at position 8 swapped.
    start = [1, 2, 3, 4, 5, 6, 7, 0, 8]

    # Run search.
    path, nodes_expanded = AStarSearch.search(
        start,
        GOAL_STATE,
        misplaced_heuristic,
    )

    # Assert the solution is exactly 1 move.
    assert len(path) == 2
    assert path[0] == start
    assert path[-1] == GOAL_STATE


# ** test: search_known_solution
def test_search_known_solution() -> None:
    '''
    Test A* search on a known puzzle configuration requiring 3 moves.

    Configuration: [1, 2, 3, 0, 5, 6, 4, 7, 8]
    Optimal path (3 moves):
        [1,2,3,0,5,6,4,7,8] -> [1,2,3,4,5,6,0,7,8] ->
        [1,2,3,4,5,6,7,0,8] -> [1,2,3,4,5,6,7,8,0]
    '''

    # Start: a configuration that requires 3 moves to solve.
    start = [1, 2, 3, 0, 5, 6, 4, 7, 8]

    # Run search.
    path, nodes_expanded = AStarSearch.search(
        start,
        GOAL_STATE,
        misplaced_heuristic,
    )

    # Assert the path starts at start and ends at goal.
    assert path[0] == start
    assert path[-1] == GOAL_STATE

    # Assert the solution is optimal (3 moves).
    assert len(path) - 1 == 3

    # Assert nodes were expanded.
    assert nodes_expanded >= 1
