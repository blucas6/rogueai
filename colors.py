import curses

class Colors:
    '''
    Colors class sets up the colors for the curses interface
    '''
    _instance = None
    
    def __new__(obj):
        if not obj._instance:
            obj._instance = super(Colors, obj).__new__(obj)
            obj._instance.setColors()
        return obj._instance
    
    def setColors(self):
        '''
        Set up the color pairs for the curses interface
        '''
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.black = curses.color_pair(1)
        self.red = curses.color_pair(2)
        self.green = curses.color_pair(3)
        self.yellow = curses.color_pair(4)
        self.blue = curses.color_pair(5)
        self.magenta = curses.color_pair(6)
        self.cyan = curses.color_pair(7)
        self.white = curses.color_pair(8)
        self.white_inv = curses.color_pair(9)