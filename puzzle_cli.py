# *** imports

# ** infra
from tiferet import App


# *** main

# Create new app instance.
app = App()

# Load the CLI app instance.
cli = app.load_interface('puzzle_cli')


# * method: main
def main():
    '''
    Entry point for the puzzle CLI.
    '''

    # Run the CLI app.
    cli.run()


# Run the CLI app.
if __name__ == '__main__':
    main()
