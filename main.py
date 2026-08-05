from parsing import pars_file
from drone import ControlDrone
from py_game.scren import Screen
import pygame

def main():
    files_parsing = pars_file("maps/medium/02_circular_loop.txt")
    # display_screen = Screen(files_parsing)
    # display_screen.display()

if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print(e)