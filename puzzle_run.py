from tiferet import App, TiferetError

# Initialize the Tiferet application.
app = App()

# Define test cases: (label, start_state, goal_state)
test_cases = [
    ('Trivial (solved)',        '1,2,3,4,5,6,7,8,*', '1,2,3,4,5,6,7,8,*'),
    ('Easy (2 moves)',          '1,2,3,4,5,6,7,*,8', '1,2,3,4,5,6,7,8,*'),
    ('Easy (3 moves)',          '1,2,3,4,5,6,*,7,8', '1,2,3,4,5,6,7,8,*'),
    ('Medium (10+ moves)',      '2,8,3,1,6,4,7,*,5', '1,2,3,8,*,4,7,6,5'),
    ('Medium (custom goal)',    '1,3,4,8,6,2,7,*,5', '1,2,3,8,*,4,7,6,5'),
    ('Hard (20+ moves)',        '8,6,7,2,5,4,3,*,1', '1,2,3,4,5,6,7,8,*'),
    ('Hard (scrambled)',        '6,1,8,4,*,2,7,3,5', '1,2,3,4,5,6,7,8,*'),
    ('Unsolvable',              '1,2,3,4,5,6,8,7,*', '1,2,3,4,5,6,7,8,*'),
]

# Heuristics to compare.
heuristics = ['misplaced', 'manhattan', 'linear-conflict', 'pattern-db']

# Print header.
print('=' * 80)
print('8-PUZZLE A* SOLVER — HEURISTIC COMPARISON')
print('=' * 80)

# Run each test case with each heuristic.
for label, start, goal in test_cases:
    print(f'\n{"—" * 80}')
    print(f'Test: {label}')
    print(f'Start: {start}')
    print(f'Goal:  {goal}')
    print(f'{"—" * 80}')

    for h in heuristics:
        try:
            result = app.run(
                'puzzle_solver',
                'puzzle.solve',
                data=dict(start=start, goal=goal, heuristic=h),
            )
            print(f'\n[{h.upper()}]')
            print(result)
        except TiferetError as e:
            print(f'\n[{h.upper()}] Error: {e.message if hasattr(e, "message") else e}')
        except Exception as e:
            print(f'\n[{h.upper()}] Error: {e}')

print(f'\n{"=" * 80}')
print('Comparison complete.')
