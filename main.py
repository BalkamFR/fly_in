from parsing import pars_file
from py_game.scren import Screen

def main():
    files_parsing = pars_file("maps/hard/01_maze_nightmare.txt")
    display_screen = Screen(files_parsing)
    display_screen.display()

if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print(e)