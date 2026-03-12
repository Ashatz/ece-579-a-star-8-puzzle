# *** imports

# ** infra
import pytest

# ** app
from app.utils.pdb import PatternDatabase, PDB_TILES_1, PDB_TILES_2, _PDB_CACHE


# *** constants

# ** constant: goal_state
GOAL_STATE = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# ** constant: goal_tuple
GOAL_TUPLE = tuple(GOAL_STATE)


# *** tests

# ** test: abstract_state
def test_abstract_state() -> None:
    '''
    Test abstract state extraction for pattern {1,2,3,4} from the goal state.
    In the goal [1,2,3,4,5,6,7,8,0], blank is at 8, tiles 1-4 are at 0-3.
    '''

    # Extract the abstract state for pattern 1 from the goal.
    result = PatternDatabase.abstract_state(GOAL_STATE, PDB_TILES_1)

    # Assert: (blank_pos=8, tile1_pos=0, tile2_pos=1, tile3_pos=2, tile4_pos=3).
    assert result == (8, 0, 1, 2, 3)


# ** test: abstract_state_pattern_2
def test_abstract_state_pattern_2() -> None:
    '''
    Test abstract state extraction for pattern {5,6,7,8} from the goal state.
    In the goal [1,2,3,4,5,6,7,8,0], blank is at 8, tiles 5-8 are at 4-7.
    '''

    # Extract the abstract state for pattern 2 from the goal.
    result = PatternDatabase.abstract_state(GOAL_STATE, PDB_TILES_2)

    # Assert: (blank_pos=8, tile5_pos=4, tile6_pos=5, tile7_pos=6, tile8_pos=7).
    assert result == (8, 4, 5, 6, 7)


# ** test: abstract_state_scrambled
def test_abstract_state_scrambled() -> None:
    '''
    Test abstract state extraction from a scrambled state.
    State [2,8,3,1,6,4,7,0,5]: blank at 7, tile 1 at 3, tile 2 at 0,
    tile 3 at 2, tile 4 at 5.
    '''

    # Extract the abstract state for pattern 1 from a scrambled state.
    state = [2, 8, 3, 1, 6, 4, 7, 0, 5]
    result = PatternDatabase.abstract_state(state, PDB_TILES_1)

    # Assert: (blank_pos=7, tile1_pos=3, tile2_pos=0, tile3_pos=2, tile4_pos=5).
    assert result == (7, 3, 0, 2, 5)


# ** test: precompute_goal_entry
def test_precompute_goal_entry() -> None:
    '''
    Test that precomputing a PDB for the goal state has distance 0
    at the goal abstract state.
    '''

    # Precompute the PDB for pattern {1,2,3,4} from the goal.
    distances = PatternDatabase.precompute({1, 2, 3, 4}, GOAL_TUPLE)

    # The goal abstract state should have distance 0.
    goal_abstract = PatternDatabase.abstract_state(GOAL_TUPLE, PDB_TILES_1)
    assert distances[goal_abstract] == 0


# ** test: precompute_nonempty
def test_precompute_nonempty() -> None:
    '''
    Test that precomputing a PDB produces a non-trivial number of entries.
    The 4-tile pattern on a 3x3 grid should produce thousands of reachable
    abstract states.
    '''

    # Precompute the PDB for pattern {1,2,3,4}.
    distances = PatternDatabase.precompute({1, 2, 3, 4}, GOAL_TUPLE)

    # Assert the table has a substantial number of entries.
    assert len(distances) > 1000


# ** test: get_tables_returns_pair
def test_get_tables_returns_pair() -> None:
    '''
    Test that get_tables returns a pair of non-empty dicts.
    '''

    # Clear cache to ensure fresh computation.
    _PDB_CACHE.clear()

    # Get tables for the standard goal.
    pdb1, pdb2 = PatternDatabase.get_tables(GOAL_TUPLE)

    # Assert both are non-empty dicts.
    assert isinstance(pdb1, dict) and len(pdb1) > 0
    assert isinstance(pdb2, dict) and len(pdb2) > 0


# ** test: get_tables_caching
def test_get_tables_caching() -> None:
    '''
    Test that get_tables caches results and returns the same objects
    on subsequent calls.
    '''

    # Clear cache to start fresh.
    _PDB_CACHE.clear()

    # First call computes the tables.
    result1 = PatternDatabase.get_tables(GOAL_TUPLE)

    # Second call should return the cached objects.
    result2 = PatternDatabase.get_tables(GOAL_TUPLE)

    # Assert the returned objects are identical (same reference).
    assert result1[0] is result2[0]
    assert result1[1] is result2[1]

    # Assert the goal is in the cache.
    assert GOAL_TUPLE in _PDB_CACHE


# ** test: lookup_goal
def test_lookup_goal() -> None:
    '''
    Test that looking up the goal state returns heuristic value 0.
    '''

    # Look up the goal state against itself.
    result = PatternDatabase.lookup(GOAL_STATE, GOAL_STATE)

    # Assert the heuristic value is 0 (already at goal).
    assert result == 0


# ** test: lookup_nongoal
def test_lookup_nongoal() -> None:
    '''
    Test that looking up a non-goal state returns a positive heuristic value.
    '''

    # A scrambled state that is not the goal.
    state = [2, 8, 3, 1, 6, 4, 7, 0, 5]

    # Look up the heuristic value.
    result = PatternDatabase.lookup(state, GOAL_STATE)

    # Assert the heuristic value is positive (tiles are displaced).
    assert result > 0


# ** test: lookup_admissible
def test_lookup_admissible() -> None:
    '''
    Test that the PDB heuristic is admissible by verifying it does not
    exceed the known optimal solution length for a test case.

    State [1,2,3,0,5,6,4,7,8] has optimal solution length 3.
    '''

    # A state with known optimal solution length of 3.
    state = [1, 2, 3, 0, 5, 6, 4, 7, 8]

    # Look up the heuristic value.
    result = PatternDatabase.lookup(state, GOAL_STATE)

    # Assert the heuristic is admissible (does not exceed optimal cost).
    assert result <= 3
    assert result > 0
