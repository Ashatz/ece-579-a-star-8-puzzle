# *** imports

# ** infra
import pytest
from tiferet import TiferetError
from tiferet.events import DomainEvent

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

# ** test: solve_puzzle_manhattan
def test_solve_puzzle_manhattan() -> None:
    '''
    Test solving a puzzle with the manhattan heuristic.
    '''

    # Execute the solve puzzle event with manhattan heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='manhattan',
    )

    # Assert the result contains expected output markers.
    assert 'Heuristic: manhattan' in result
    assert 'Moves: 1' in result
    assert 'Nodes expanded:' in result
    assert 'Time:' in result


# ** test: solve_puzzle_misplaced
def test_solve_puzzle_misplaced() -> None:
    '''
    Test solving a puzzle with the misplaced heuristic.
    '''

    # Execute the solve puzzle event with misplaced heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='misplaced',
    )

    # Assert the result contains expected output markers.
    assert 'Heuristic: misplaced' in result
    assert 'Moves: 1' in result


# ** test: solve_puzzle_linear_conflict
def test_solve_puzzle_linear_conflict() -> None:
    '''
    Test solving a puzzle with the linear-conflict heuristic.
    '''

    # Execute the solve puzzle event with linear-conflict heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='linear-conflict',
    )

    # Assert the result contains expected output markers.
    assert 'Heuristic: linear-conflict' in result
    assert 'Moves: 1' in result


# ** test: solve_puzzle_pattern_db
def test_solve_puzzle_pattern_db() -> None:
    '''
    Test solving a puzzle with the pattern-db heuristic.
    '''

    # Execute the solve puzzle event with pattern-db heuristic.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SOLVABLE_START,
        goal=GOAL_STRING,
        heuristic='pattern-db',
    )

    # Assert the result contains expected output markers.
    assert 'Heuristic: pattern-db' in result
    assert 'Moves: 1' in result


# ** test: solve_puzzle_already_solved
def test_solve_puzzle_already_solved() -> None:
    '''
    Test solving a puzzle where start equals goal (zero moves).
    '''

    # Execute the solve puzzle event with start == goal.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=GOAL_STRING,
        goal=GOAL_STRING,
        heuristic='manhattan',
    )

    # Assert the result shows zero moves.
    assert 'Moves: 0' in result
    assert 'Nodes expanded: 1' in result


# ** test: solve_puzzle_scrambled
def test_solve_puzzle_scrambled() -> None:
    '''
    Test solving a more complex scrambled puzzle configuration.
    Verifies that a multi-step solution is found.
    '''

    # Execute the solve puzzle event with a scrambled start.
    result = DomainEvent.handle(
        SolvePuzzle,
        start=SCRAMBLED_START,
        goal=GOAL_STRING,
        heuristic='manhattan',
    )

    # Assert the result contains expected output markers.
    assert 'Heuristic: manhattan' in result
    assert 'Moves:' in result
    assert 'Step 0:' in result


# ** test: solve_puzzle_invalid_heuristic
def test_solve_puzzle_invalid_heuristic() -> None:
    '''
    Test that an invalid heuristic raises INVALID_HEURISTIC.
    '''

    # Attempt to solve with an unsupported heuristic.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SolvePuzzle,
            start=SOLVABLE_START,
            goal=GOAL_STRING,
            heuristic='bogus',
        )

    # Assert the error code is INVALID_HEURISTIC.
    assert exc_info.value.error_code == 'INVALID_HEURISTIC'


# ** test: solve_puzzle_invalid_state
def test_solve_puzzle_invalid_state() -> None:
    '''
    Test that an invalid start state raises INVALID_STATE.
    '''

    # Attempt to solve with a non-numeric start state.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SolvePuzzle,
            start='a,b,c,d,e,f,g,h,i',
            goal=GOAL_STRING,
            heuristic='manhattan',
        )

    # Assert the error code is INVALID_STATE.
    assert exc_info.value.error_code == 'INVALID_STATE'


# ** test: solve_puzzle_unsolvable
def test_solve_puzzle_unsolvable() -> None:
    '''
    Test that an unsolvable configuration raises UNSOLVABLE_STATE.
    '''

    # Attempt to solve an unsolvable configuration.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            SolvePuzzle,
            start=UNSOLVABLE_START,
            goal=GOAL_STRING,
            heuristic='manhattan',
        )

    # Assert the error code is UNSOLVABLE_STATE.
    assert exc_info.value.error_code == 'UNSOLVABLE_STATE'
