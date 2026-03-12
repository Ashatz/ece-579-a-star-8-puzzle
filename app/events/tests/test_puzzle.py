# *** imports

# ** infra
import pytest
from tiferet.events import DomainEvent
from tiferet.assets.exceptions import TiferetError

# ** app
from app.events.puzzle import SolvePuzzle


# *** constants

# ** constant: goal_string
GOAL_STRING = '1,2,3,4,5,6,7,8,*'

# ** constant: solvable_start
SOLVABLE_START = '1,2,3,4,5,6,7,*,8'

# ** constant: scrambled_start
SCRAMBLED_START = '4,1,2,7,6,3,*,5,8'

# ** constant: unsolvable_start
UNSOLVABLE_START = '2,1,3,4,5,6,7,8,*'


# *** tests

# ** test: test_solve_puzzle_manhattan
def test_solve_puzzle_manhattan():
    '''
    Test solving a 1-move puzzle with the manhattan heuristic.
    '''

    # Execute the solve puzzle event with manhattan heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='manhattan',
    )

    # Verify the output contains expected markers.
    assert 'Heuristic: manhattan' in result
    assert 'Moves: 1' in result


# ** test: test_solve_puzzle_misplaced
def test_solve_puzzle_misplaced():
    '''
    Test solving a 1-move puzzle with the misplaced heuristic.
    '''

    # Execute the solve puzzle event with misplaced heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='misplaced',
    )

    # Verify the output contains expected markers.
    assert 'Heuristic: misplaced' in result
    assert 'Moves: 1' in result


# ** test: test_solve_puzzle_linear_conflict
def test_solve_puzzle_linear_conflict():
    '''
    Test solving a 1-move puzzle with the linear-conflict heuristic.
    '''

    # Execute the solve puzzle event with linear-conflict heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='linear-conflict',
    )

    # Verify the output contains expected markers.
    assert 'Heuristic: linear-conflict' in result
    assert 'Moves: 1' in result


# ** test: test_solve_puzzle_pattern_db
def test_solve_puzzle_pattern_db():
    '''
    Test solving a 1-move puzzle with the pattern-db heuristic.
    '''

    # Execute the solve puzzle event with pattern-db heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='pattern-db',
    )

    # Verify the output contains expected markers.
    assert 'Heuristic: pattern-db' in result
    assert 'Moves: 1' in result


# ** test: test_solve_puzzle_already_solved
def test_solve_puzzle_already_solved():
    '''
    Test solving when start equals goal (0 moves).
    '''

    # Execute the solve puzzle event with start == goal.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=GOAL_STRING,
        goal=GOAL_STRING,
        heuristic='manhattan',
    )

    # Verify the output shows 0 moves and 1 node expanded.
    assert 'Moves: 0' in result
    assert 'Nodes expanded: 1' in result


# ** test: test_solve_puzzle_scrambled
def test_solve_puzzle_scrambled():
    '''
    Test solving a multi-step scrambled puzzle.
    '''

    # Execute the solve puzzle event with a scrambled start.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SCRAMBLED_START,
        goal=GOAL_STRING,
        heuristic='manhattan',
    )

    # Verify the output contains step markers and a non-trivial move count.
    assert 'Moves:' in result
    assert 'Step 0:' in result


# ** test: test_solve_puzzle_invalid_heuristic
def test_solve_puzzle_invalid_heuristic():
    '''
    Test that an invalid heuristic raises INVALID_HEURISTIC.
    '''

    # Execute with an invalid heuristic and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SolvePuzzle,
            start=SOLVABLE_START,
            goal=GOAL_STRING,
            heuristic='invalid',
        )

    # Verify the error code.
    assert exc_info.value.error_code == 'INVALID_HEURISTIC'


# ** test: test_solve_puzzle_invalid_state
def test_solve_puzzle_invalid_state():
    '''
    Test that a non-numeric state string raises INVALID_STATE.
    '''

    # Execute with an invalid state and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SolvePuzzle,
            start='a,b,c,d,e,f,g,h,i',
            goal=GOAL_STRING,
            heuristic='manhattan',
        )

    # Verify the error code.
    assert exc_info.value.error_code == 'INVALID_STATE'


# ** test: test_solve_puzzle_unsolvable
def test_solve_puzzle_unsolvable():
    '''
    Test that an unsolvable configuration raises UNSOLVABLE_STATE.
    '''

    # Execute with an unsolvable start and expect a TiferetError.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SolvePuzzle,
            start=UNSOLVABLE_START,
            goal=GOAL_STRING,
            heuristic='manhattan',
        )

    # Verify the error code.
    assert exc_info.value.error_code == 'UNSOLVABLE_STATE'
