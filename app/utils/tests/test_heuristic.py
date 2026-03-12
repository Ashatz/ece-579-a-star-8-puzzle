# *** imports

# ** infra
import pytest

# ** app
from app.utils.heuristic import HeuristicCalculator


# *** constants

# ** constant: goal_state
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# ** constant: scrambled_state
SCRAMBLED_STATE = [2, 8, 3, 1, 6, 4, 7, 0, 5]

# ** constant: one_move_state
ONE_MOVE_STATE = [1, 2, 3, 4, 5, 6, 7, 0, 8]


# *** tests

# ** test: misplaced_goal
def test_misplaced_goal() -> None:
    '''
    Test that misplaced returns 0 when state equals goal.
    '''

    # Compute misplaced tiles for the goal state.
    result = HeuristicCalculator.misplaced(GOAL_STATE, GOAL_STATE)

    # Assert no tiles are misplaced.
    assert result == 0


# ** test: misplaced_nongoal
def test_misplaced_nongoal() -> None:
    '''
    Test that misplaced returns a positive count for a non-goal state.
    '''

    # Compute misplaced tiles for a scrambled state.
    result = HeuristicCalculator.misplaced(SCRAMBLED_STATE, GOAL_STATE)

    # Assert at least one tile is misplaced.
    assert result > 0


# ** test: misplaced_one_move
def test_misplaced_one_move() -> None:
    '''
    Test misplaced tiles for a state one move from the goal.
    [1,2,3,4,5,6,7,0,8] — only tile 8 is misplaced.
    '''

    # Compute misplaced tiles for the one-move state.
    result = HeuristicCalculator.misplaced(ONE_MOVE_STATE, GOAL_STATE)

    # Assert exactly 1 tile is misplaced (tile 8).
    assert result == 1


# ** test: manhattan_goal
def test_manhattan_goal() -> None:
    '''
    Test that manhattan returns 0 when state equals goal.
    '''

    # Compute Manhattan distance for the goal state.
    result = HeuristicCalculator.manhattan(GOAL_STATE, GOAL_STATE)

    # Assert distance is 0.
    assert result == 0


# ** test: manhattan_nongoal
def test_manhattan_nongoal() -> None:
    '''
    Test that manhattan returns a positive distance for a non-goal state.
    '''

    # Compute Manhattan distance for a scrambled state.
    result = HeuristicCalculator.manhattan(SCRAMBLED_STATE, GOAL_STATE)

    # Assert distance is positive.
    assert result > 0


# ** test: manhattan_one_move
def test_manhattan_one_move() -> None:
    '''
    Test Manhattan distance for a state one move from the goal.
    [1,2,3,4,5,6,7,0,8] — tile 8 is 1 position away.
    '''

    # Compute Manhattan distance for the one-move state.
    result = HeuristicCalculator.manhattan(ONE_MOVE_STATE, GOAL_STATE)

    # Assert distance is exactly 1.
    assert result == 1


# ** test: manhattan_admissible
def test_manhattan_admissible() -> None:
    '''
    Test that Manhattan is admissible: h(state) <= actual optimal cost.
    State [1,2,3,0,5,6,4,7,8] has optimal solution length 3.
    '''

    # A state with known optimal solution length of 3.
    state = [1, 2, 3, 0, 5, 6, 4, 7, 8]

    # Compute Manhattan distance.
    result = HeuristicCalculator.manhattan(state, GOAL_STATE)

    # Assert admissibility (does not exceed optimal cost).
    assert result <= 3
    assert result > 0


# ** test: linear_conflict_no_conflict
def test_linear_conflict_no_conflict() -> None:
    '''
    Test that linear_conflict equals manhattan when there are no
    linear conflicts. For the one-move state [1,2,3,4,5,6,7,0,8],
    tile 8 is in row 2 and its goal is row 2, but there is no
    reversed pair, so conflict penalty is 0.
    '''

    # Compute linear conflict for the one-move state.
    lc = HeuristicCalculator.linear_conflict(ONE_MOVE_STATE, GOAL_STATE)

    # Compute Manhattan for comparison.
    m = HeuristicCalculator.manhattan(ONE_MOVE_STATE, GOAL_STATE)

    # Assert linear conflict equals Manhattan (no conflict penalty).
    assert lc == m


# ** test: linear_conflict_with_conflict
def test_linear_conflict_with_conflict() -> None:
    '''
    Test that linear_conflict exceeds manhattan when there is a
    linear conflict. State [2,1,3,4,5,6,7,8,0] has tiles 1 and 2
    in row 0, both belonging to row 0 but reversed — one conflict
    adding +2.
    '''

    # A state with a row-0 linear conflict (tiles 2,1 reversed).
    state = [2, 1, 3, 4, 5, 6, 7, 8, 0]

    # Compute linear conflict.
    lc = HeuristicCalculator.linear_conflict(state, GOAL_STATE)

    # Compute Manhattan for comparison.
    m = HeuristicCalculator.manhattan(state, GOAL_STATE)

    # Assert linear conflict is strictly greater (conflict penalty applied).
    assert lc > m

    # The conflict penalty should be exactly +2 for one reversed pair.
    assert lc == m + 2


# ** test: linear_conflict_goal
def test_linear_conflict_goal() -> None:
    '''
    Test that linear_conflict returns 0 when state equals goal.
    '''

    # Compute linear conflict for the goal state.
    result = HeuristicCalculator.linear_conflict(GOAL_STATE, GOAL_STATE)

    # Assert value is 0.
    assert result == 0


# ** test: linear_conflict_admissible
def test_linear_conflict_admissible() -> None:
    '''
    Test that linear conflict is admissible and dominates Manhattan.
    '''

    # Compute both heuristics for the scrambled state.
    lc = HeuristicCalculator.linear_conflict(SCRAMBLED_STATE, GOAL_STATE)
    m = HeuristicCalculator.manhattan(SCRAMBLED_STATE, GOAL_STATE)

    # Assert linear conflict is at least Manhattan (dominance).
    assert lc >= m


# ** test: pattern_db_goal
def test_pattern_db_goal() -> None:
    '''
    Test that pattern_db returns 0 when state equals goal.
    '''

    # Compute PDB heuristic for the goal state.
    result = HeuristicCalculator.pattern_db(GOAL_STATE, GOAL_STATE)

    # Assert the heuristic value is 0.
    assert result == 0


# ** test: pattern_db_nongoal
def test_pattern_db_nongoal() -> None:
    '''
    Test that pattern_db returns a positive value for a non-goal state.
    '''

    # Compute PDB heuristic for a scrambled state.
    result = HeuristicCalculator.pattern_db(SCRAMBLED_STATE, GOAL_STATE)

    # Assert the heuristic value is positive.
    assert result > 0


# ** test: pattern_db_admissible
def test_pattern_db_admissible() -> None:
    '''
    Test that pattern_db is admissible: h(state) <= actual optimal cost.
    State [1,2,3,0,5,6,4,7,8] has optimal solution length 3.
    '''

    # A state with known optimal solution length of 3.
    state = [1, 2, 3, 0, 5, 6, 4, 7, 8]

    # Compute PDB heuristic.
    result = HeuristicCalculator.pattern_db(state, GOAL_STATE)

    # Assert admissibility (does not exceed optimal cost).
    assert result <= 3
    assert result > 0
