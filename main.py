import curses
from game import Game

if __name__ == '__main__':
    g = Game()
    curses.wrapper(g.start)