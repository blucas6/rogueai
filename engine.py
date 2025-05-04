import curses
import traceback
from colors import Colors

class Engine:
    '''
    Engine class provides a curses interface displayer
    Pass any 2D character buffer and display it with colors
    '''
    def __init__(self):
        self.inputTimeout = 1
        '''optional ms between engine display'''
        self.stdscr = None
        '''curses.window'''
        self.ErrorLog = 'ErrorLog.log'
        '''where to dump errors'''
        self.EventLog = 'EventLog.log'
        '''where to dump events'''
        self.FrameDelay = 1
        '''optional delay between frames'''
        self.Frames = 0
        '''current frame counter'''
        self.Initialized = False
        '''keeps track of object initialization of the curses module'''

    def frameReady(self):
        '''
        Decrement frame counter and return if engine is ready to display
        '''
        self.Frames -= 1
        if self.Frames <= 0:
            self.Frames = self.FrameDelay
            return True
        return False

    def init(self, stdscr: curses.window, timeDelay: int=None):
        '''
        Required to call at engine startup, returns size of terminal
        '''
        curses.start_color()
        self.Colors = Colors()
        self.stdscr = stdscr
        self.termrows, self.termcols = stdscr.getmaxyx()
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(self.inputTimeout)
        if timeDelay:
            self.FrameDelay = timeDelay
        # clear logs
        with open(self.ErrorLog, 'w+') as el:
            el.write('')
        with open(self.EventLog, 'w+') as el:
            el.write('')
        self.Initialized = True
        self.logEvent(f'Engine initialized {(self.termrows,self.termcols)}')
        self.logEvent(f'  Frame Delay: {self.FrameDelay}')
        return self.termrows, self.termcols

    def output(self, screenChars: list=[], screenColors: list=[]):
        '''
        Call to output a 2D character buffer and an optional 2D curses
        color pair buffer to the terminal
        '''
        if not self.Initialized:
            return
        try:
            for r,row in enumerate(screenChars):
                for c,chr in enumerate(row):
                    if r < len(screenColors) and c < len(screenColors[r]):
                        color = screenColors[r][c]
                    else:
                        color = self.Colors.white
                    self.stdscr.addch(r, c, chr, color)
            self.stdscr.refresh()
        except Exception as e:
            self.logError(f'Display ERROR: [{c},{r}]: {e}')
    
    def readInput(self):
        '''
        Call to grab input and return a valid event in string form
        '''
        if not self.Initialized:
            return
        try:
            event = self.stdscr.getch()
            if event != curses.ERR:
                #self.logEvent(chr(event))
                return chr(event)
        except Exception as e:
            self.logError(f'Read input ERROR: {event}')
    
    def logEvent(self, msg):
        with open(self.EventLog, 'a+') as lf:
            lf.write(f'{msg}\n')

    def logError(self, msg=''):
        with open(self.ErrorLog, 'a+') as lf:
            lf.write(f'{traceback.format_exc()}')
            lf.write(f'{msg}\n')

    def cursorPosition(self, pos):
        '''
        Moves the cursor to a position
        '''
        if not self.Initialized:
            return
        if pos[0] < self.termrows and pos[1] < self.termcols:
            self.stdscr.move(pos[0], pos[1])
        else:
            self.logError(f'Invalid cursor position {pos}')