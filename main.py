import sys
from parsing import pars_file
from py_game.scren import Screen


def main():
    files_parsing = None
    if len(sys.argv) > 1:
        path_map = sys.argv[1]
        files_parsing = pars_file(path_map)

    display_screen = Screen(files_parsing)
    display_screen.display()


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print(e)
