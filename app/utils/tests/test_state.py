# *** imports

# ** infra
import pytest

# ** app
from tiferet import TiferetError
from app.utils.state import PuzzleStateParser


# *** fixtures

# ** fixture: goal_state
@pytest.fixture
def goal_state() -> list:
    '''
    Standard goal state for the 8-puzzle.
    '''
    return [1, 2, 3, 4, 5, 6, 7, 8, 0]


# ** fixture: solvable_state
@pytest.fixture
def solvable_state() -> list:
    '''
    A solvable start state (even inversion parity relative to standard goal).
    '''
    return [1, 2, 3, 4, 5, 0, 7, 8, 6]


# ** fixture: unsolvable_state
@pytest.fixture
def unsolvable_state() -> list:
    '''
    An unsolvable start state (odd inversion parity relative to standard goal).
    '''
    return [1, 2, 3, 4, 5, 6, 8, 7, 0]


# *** tests

# ** test: parse_state_comma_separated
def test_parse_state_comma_separated() -> None:
    '''
    Test parsing a comma-separated state string.
    '''

    # Parse a comma-separated state string.
    result = PuzzleStateParser.parse_state('1,2,3,4,5,6,7,8,*')

    # Assert the parsed result matches expected output.
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 0]


# ** test: parse_state_space_separated
def test_parse_state_space_separated() -> None:
    '''
    Test parsing a space-separated state string.
    '''

    # Parse a space-separated state string.
    result = PuzzleStateParser.parse_state('1 2 3 4 5 6 7 8 *')

    # Assert the parsed result matches expected output.
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 0]


# ** test: parse_state_contiguous
def test_parse_state_contiguous() -> None:
    '''
    Test parsing a 9-character contiguous state string.
    '''

    # Parse a contiguous state string.
    result = PuzzleStateParser.parse_state('123456780')

    # Assert the parsed result matches expected output.
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 0]


# ** test: parse_state_blank_symbol
def test_parse_state_blank_symbol() -> None:
    '''
    Test that the blank symbol * is normalized to 0.
    '''

    # Parse a state string with * as blank.
    result = PuzzleStateParser.parse_state('*,1,2,3,4,5,6,7,8')

    # Assert the blank was normalized to 0.
    assert result == [0, 1, 2, 3, 4, 5, 6, 7, 8]


# ** test: parse_state_invalid
def test_parse_state_invalid() -> None:
    '''
    Test that parsing an invalid state string raises INVALID_STATE.
    '''

    # Attempt to parse a non-numeric state string.
    with pytest.raises(TiferetError) as exc_info:
        PuzzleStateParser.parse_state('a,b,c,d,e,f,g,h,i')

    # Assert the error code is INVALID_STATE.
    assert exc_info.value.error_code == 'INVALID_STATE'


# ** test: verify_state_valid
def test_verify_state_valid(goal_state: list) -> None:
    '''
    Test that a valid state passes verification.

    :param goal_state: The standard goal state.
    :type goal_state: list
    '''

    # Verify a valid state does not raise.
    PuzzleStateParser.verify_state(goal_state)


# ** test: verify_state_wrong_length
def test_verify_state_wrong_length() -> None:
    '''
    Test that a state with wrong length raises INVALID_STATE.
    '''

    # Attempt to verify a state with too few tiles.
    with pytest.raises(TiferetError) as exc_info:
        PuzzleStateParser.verify_state([1, 2, 3])

    # Assert the error code is INVALID_STATE.
    assert exc_info.value.error_code == 'INVALID_STATE'


# ** test: verify_state_duplicate_tile
def test_verify_state_duplicate_tile() -> None:
    '''
    Test that a state with duplicate tile values raises INVALID_STATE.
    '''

    # Attempt to verify a state with a duplicate tile.
    with pytest.raises(TiferetError) as exc_info:
        PuzzleStateParser.verify_state([1, 1, 3, 4, 5, 6, 7, 8, 0])

    # Assert the error code is INVALID_STATE.
    assert exc_info.value.error_code == 'INVALID_STATE'


# ** test: is_solvable_true
def test_is_solvable_true(solvable_state: list, goal_state: list) -> None:
    '''
    Test that a solvable state returns True.

    :param solvable_state: A solvable start state.
    :type solvable_state: list
    :param goal_state: The standard goal state.
    :type goal_state: list
    '''

    # Check solvability of a solvable state.
    result = PuzzleStateParser.is_solvable(solvable_state, goal_state)

    # Assert the state is solvable.
    assert result is True


# ** test: is_solvable_false
def test_is_solvable_false(unsolvable_state: list, goal_state: list) -> None:
    '''
    Test that an unsolvable state returns False.

    :param unsolvable_state: An unsolvable start state.
    :type unsolvable_state: list
    :param goal_state: The standard goal state.
    :type goal_state: list
    '''

    # Check solvability of an unsolvable state.
    result = PuzzleStateParser.is_solvable(unsolvable_state, goal_state)

    # Assert the state is unsolvable.
    assert result is False


# ** test: format_grid
def test_format_grid(goal_state: list) -> None:
    '''
    Test grid formatting with default blank symbol.

    :param goal_state: The standard goal state.
    :type goal_state: list
    '''

    # Format the goal state as a grid.
    result = PuzzleStateParser.format_grid(goal_state)

    # Assert the grid matches expected output.
    assert result == '1 2 3\n4 5 6\n7 8 *'


# ** test: format_grid_custom_blank
def test_format_grid_custom_blank(goal_state: list) -> None:
    '''
    Test grid formatting with a custom blank symbol.

    :param goal_state: The standard goal state.
    :type goal_state: list
    '''

    # Format the goal state with a custom blank symbol.
    result = PuzzleStateParser.format_grid(goal_state, blank_symbol='_')

    # Assert the grid uses the custom blank symbol.
    assert result == '1 2 3\n4 5 6\n7 8 _'
