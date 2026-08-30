from py_game.scren import Screen

def main():
    display_screen = Screen()
    display_screen.display()

if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print(e)