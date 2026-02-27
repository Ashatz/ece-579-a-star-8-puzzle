from tiferet import App

# Create new app (manager) instance.
app = App()

# Load the CLI app instance.
cli = app.load_interface('puzzle_cli')

# Run the CLI app.
if __name__ == '__main__':
    cli.run()
