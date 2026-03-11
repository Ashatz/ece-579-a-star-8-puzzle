# *** imports

# ** infra
import pytest
from tiferet import TiferetError

# ** app
from app.utils.state import PuzzleStateParser


# *** constants

# ** constant: goal_state
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]


# *** tests

# ** test: parse_state_comma_separated
def test_parse_state_comma_separated() -> None:
    '''
    Test parsing a comma-separated state string.
    '''

    # Parse a comma-separated state string.
    result = PuzzleStateParser.parse_state('2,8,3,1,6,4,7,0,5')

    # Assert the parsed state matches the expected list.
    assert result == [2, 8, 3, 1, 6, 4, 7, 0, 5]


# ** test: parse_state_space_separated
def test_parse_state_space_separated() -> None:
    '''
    Test parsing a space-separated state string.
    '''

    # Parse a space-separated state string.
    result = PuzzleStateParser.parse_state('2 8 3 1 6 4 7 0 5')

    # Assert the parsed state matches the expected list.
    assert result == [2, 8, 3, 1, 6, 4, 7, 0, 5]


# ** test: parse_state_contiguous
def test_parse_state_contiguous() -> None:
    '''
    Test parsing a contiguous 9-character state string.
    '''

    # Parse a contiguous state string.
    result = PuzzleStateParser.parse_state('283164705')

    # Assert the parsed state matches the expected list.
    assert result == [2, 8, 3, 1, 6, 4, 7, 0, 5]


# ** test: parse_state_blank_symbol
def test_parse_state_blank_symbol() -> None:
    '''
    Test parsing a state string with '*' as the blank symbol.
    '''

    # Parse a state string using '*' for blank.
    result = PuzzleStateParser.parse_state('2,8,3,1,6,4,7,*,5')

    # Assert the blank is parsed as 0.
    assert result == [2, 8, 3, 1, 6, 4, 7, 0, 5]


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
def test_verify_state_valid() -> None:
    '''
    Test that a valid state passes verification without error.
    '''

    # Verify a valid state (should not raise).
    PuzzleStateParser.verify_state([1, 2, 3, 4, 5, 6, 7, 8, 0])


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

    # Attempt to verify a state with duplicate tiles.
    with pytest.raises(TiferetError) as exc_info:
        PuzzleStateParser.verify_state([1, 1, 3, 4, 5, 6, 7, 8, 0])

    # Assert the error code is INVALID_STATE.
    assert exc_info.value.error_code == 'INVALID_STATE'


# ** test: is_solvable_true
def test_is_solvable_true() -> None:
    '''
    Test that a solvable configuration returns True.
    '''

    # Check a known solvable configuration against the standard goal.
    # [1,2,3,4,5,0,7,8,6] is one move from goal (2 inversions, even parity).
    result = PuzzleStateParser.is_solvable(
        [1, 2, 3, 4, 5, 0, 7, 8, 6],
        GOAL_STATE,
    )

    # Assert the configuration is solvable.
    assert result is True


# ** test: is_solvable_false
def test_is_solvable_false() -> None:
    '''
    Test that an unsolvable configuration returns False.
    '''

    # Check a known unsolvable configuration (swap two adjacent tiles).
    result = PuzzleStateParser.is_solvable(
        [2, 1, 3, 4, 5, 6, 7, 8, 0],
        GOAL_STATE,
    )

    # Assert the configuration is unsolvable.
    assert result is False


# ** test: format_grid
def test_format_grid() -> None:
    '''
    Test grid formatting with the default blank symbol.
    '''

    # Format the goal state as a grid.
    result = PuzzleStateParser.format_grid(GOAL_STATE)

    # Assert the grid matches the expected output.
    expected = '1 2 3\n4 5 6\n7 8 *'
    assert result == expected


# ** test: format_grid_custom_blank
def test_format_grid_custom_blank() -> None:
    '''
    Test grid formatting with a custom blank symbol.
    '''

    # Format the goal state using '0' as the blank symbol.
    result = PuzzleStateParser.format_grid(GOAL_STATE, blank_symbol='0')

    # Assert the grid uses the custom blank symbol.
    expected = '1 2 3\n4 5 6\n7 8 0'
    assert result == expected
