import curses
from curses import ascii
from engine import Engine
from level import LevelManager
from colors import Colors
from logger import Logger

class TurnMenu:
    '''Holds information about the turn'''
    def __init__(self, origin: tuple):
        self.count = 0
        self.origin = origin
        self.text = f'Turn: {self.count}'
    
    def increment(self):
        self.count += 1
        self.text = f'Turn: {self.count}'

class DepthMenu:
    '''Holds information about what depth being displayed'''
    def __init__(self, origin: tuple, z: int):
        self.origin = origin
        self.text = ''
        self.changeLevel(z)
    
    def changeLevel(self, z):
        self.text = f'Current Level: {z+1}'

class Game:
    '''
    Game class controls the entire game execution from start to finish
    '''
    def __init__(self, engineEvents=True):
        self.EngineEvents = engineEvents
        '''grab events from the engine or outside source'''
        self.Engine = Engine()
        '''connection to engine for displaying and events'''
        self.running = False
        '''if the game is running'''
        self.LevelManager = None
        '''Controls objects in each level'''
        self.ScreenBuffer = None
        '''2D buffer the size of the terminal for outputting to engine'''
        self.ColorBuffer = None
        '''2D buffer the size of the terminal for outputting to engine'''
        self.CreatureLayer = None
        '''2D buffer the size of the map, holds all moving entities'''
        self.Player = None
        '''single player object'''
        self.Turn = TurnMenu(origin=(0,0))
        '''turn counter'''
        self.DepthMenu = DepthMenu(origin=(0,10), z=0)
        '''displays the current level'''
        self.Energy = 0
        '''keeps track of how much energy to dispense to objects'''
        self.Logger = Logger()
    
    def initialize(self, stdscr: curses.window=None, timeDelay: int=None):
        '''
        Full initialization for any game
        '''
        # start running
        self.running = True
        # initialize engine
        if stdscr:
            self.maxCols, self.maxRows = self.Engine.init(stdscr, timeDelay)
        # set up objects
        self.LevelManager = LevelManager(
                                height=10,
                                width=20,
                                origin=(4,4),
                                levels=3)
        self.LevelManager.defaultSetUp()
        self.LevelManager.addPlayer([1,1], 0)
        self.ScreenBuffer = [[' ' for _ in range(self.maxRows-1)] 
                                    for _ in range(self.maxCols-1)]
        self.ColorBuffer = [[Colors().white for _ in range(self.maxRows-1)] 
                                    for _ in range(self.maxCols-1)]

    def start(self, stdscr: curses.window=None):
        '''
        Entry point for the game to start, will call the main loop after
        full initialization
        '''
        self.initialize(stdscr)
        self.main()

    def main(self):
        '''
        Main process
        '''
        while self.running:
            self.loop(self.Engine.readInput())

    def loop(self, event=None):
        '''
        Execute one loop in the game loop
        '''
        # process events
        self.Energy += self.processEvent(event)
        # update all entities
        self.LevelManager.updateCurrentLevel()
        if self.LevelManager.swapLevels():
            self.DepthMenu.changeLevel(self.LevelManager.CurrentZ)
        # display through engine
        if self.Engine.frameReady():
            # build buffers
            self.LayersToScreen()
            self.MenusToScreen()
            # output
            self.Engine.output(screenChars=self.ScreenBuffer,
                                screenColors=self.ColorBuffer)
    
    def MenusToScreen(self):
        '''
        Add menus to screen buffer
        '''
        for c,ch in enumerate(self.Turn.text):
            rw = self.Turn.origin[0]
            cl = c+self.Turn.origin[1]
            self.ScreenBuffer[rw][cl] = ch
        for c,ch in enumerate(self.DepthMenu.text):
            rw = self.DepthMenu.origin[0]
            cl = c+self.DepthMenu.origin[1]
            self.ScreenBuffer[rw][cl] = ch
    
    def LayersToScreen(self):
        '''
        Build buffers according to layer information
        '''
        entityLayer = self.LevelManager.getCurrentLevel().EntityLayer
        for r,row in enumerate(entityLayer):
            for c,col in enumerate(row):
                if (r > len(self.ScreenBuffer)-1 or 
                        c > len(self.ScreenBuffer[r])-1):
                    continue
                rw = r+self.LevelManager.origin[0]
                cl = c+self.LevelManager.origin[1]
                if not entityLayer[r][c]:
                    continue
                if len(entityLayer[r][c]) == 1:
                    idx = 0
                else:
                    idx = max(range(len(entityLayer[r][c])),
                            key=lambda i:entityLayer[r][c][i].layer)
                self.ScreenBuffer[rw][cl] = entityLayer[r][c][idx].glyph
                if (r < len(self.ColorBuffer)-1 and 
                        c < len(self.ColorBuffer[r])-1):
                    self.ColorBuffer[rw][cl] = entityLayer[r][c][idx].color
    
    def processEvent(self, event):
        '''
        Process key press event from engine, returns energy amount
        '''
        if not event:
            return 0
        self.Turn.increment()
        if event == chr(ascii.ESC) or event == 'q':
            self.running = False
            return 0
        else:
            self.LevelManager.Player.doAction(event,
                self.LevelManager.getCurrentLevel().EntityLayer)
            return 1