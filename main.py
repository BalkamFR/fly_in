import sys

from parsing import pars_file
from py_game.scren import Screen


def main() -> None:
    """Entry point for the Fly-In drone simulation.

    Reads an optional map file path from the command-line arguments,
    parses it, then launches the Pygame visual simulation. If no path is
    provided the simulator opens on the map-selection start page.

    The last positional argument (sys.argv[-1]) is treated as the map
    file path when more than one argument is given.

    Raises:
        Exception: Any unhandled exception is caught and its message
            printed to stdout before the program exits cleanly.
    """
    files_parsing = None
    if len(sys.argv) > 1:
        path_map = sys.argv[-1]
        files_parsing = pars_file(path_map)

    display_screen = Screen(files_parsing)
    display_screen.display()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
