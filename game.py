import curses
import random
from curses import ascii
from engine import Engine
from level import LevelManager
from colors import Colors
from logger import Logger
from menu import MenuManager, GameState, Messager

class Game:
    '''
    Game class controls the entire game execution from start to finish
    '''
    def __init__(self, seed=None, msgBlocking=True):
        self.Engine = Engine(debug=False)
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
        self.MenuManager = None
        '''holds all information for displaying menus'''
        self.Messager = None
        '''connection to the message queue instance'''
        self.Energy = 0
        '''keeps track of how much energy to dispense to objects'''
        self.seed = seed
        '''random seed for random calls'''
        self.MessageBlocking = msgBlocking
        '''set to true to pause on multiple messages being displayed'''
        self.Logger = Logger()
    
    def displaySetup(self, stdscr: curses.window, timeDelay: int=None):
        '''
        Sets up the display for outputting to the screen
        '''
        # initialize engine
        self.maxCols, self.maxRows = self.Engine.init(stdscr, timeDelay)
    
    def gameSetup(self):
        '''
        Sets up the game from a fresh start
        '''
        # start running
        self.running = True
        # set up objects
        self.RNG = random.Random(self.seed) if self.seed is not None else random
        self.LevelManager = LevelManager(
                                self.RNG,
                                height=6,
                                width=12,
                                origin=(4,4),
                                levels=3)
        self.MenuManager = MenuManager()
        self.Messager = Messager()
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
        self.displaySetup(stdscr)
        self.gameSetup()
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
        if self.Energy > 0:
            self.Energy -= 1
            # check for win condition
            if self.win() and self.MenuManager.State == GameState.PLAYING:
                self.Messager.addMessage('You won!')
                self.MenuManager.State = GameState.WON
            # deal with messages
            self.MenuManager.MessageMenu.update(blocking=self.MessageBlocking)
            if (self.Messager.MsgQueue and 
                                self.MenuManager.State == GameState.PLAYING):
                # still more messages to process
                self.MenuManager.State = GameState.PAUSEONMSG
            elif self.MenuManager.State == GameState.PAUSEONMSG:
                self.MenuManager.State = GameState.PLAYING
        # update all entities
        self.LevelManager.updateCurrentLevel()
        if self.LevelManager.swapLevels():
            self.MenuManager.DepthMenu.update(self.LevelManager.CurrentZ)
        # display through engine
        if self.Engine.frameReady():
            # build buffers
            self.LayersToScreen()
            self.MenuManager.display(self.ScreenBuffer)
            # output
            self.Engine.output(screenChars=self.ScreenBuffer,
                                screenColors=self.ColorBuffer)
    
    def win(self):
        '''
        Returns true if the game has been won
        '''
        if self.LevelManager.Player.z == self.LevelManager.TotalLevels-1:
            return True
        return False
    
    def LayersToScreen(self):
        '''
        Build buffers according to layer information
        '''
        entityLayer = self.LevelManager.getCurrentLevel().EntityLayer
        # go through entity layer
        for r,row in enumerate(entityLayer):
            for c,col in enumerate(row):
                if (r > len(self.ScreenBuffer)-1 or 
                        c > len(self.ScreenBuffer[r])-1):
                    continue
                rw = r+self.LevelManager.origin[0]
                cl = c+self.LevelManager.origin[1]
                if not entityLayer[r][c]:
                    continue
                # find top most entity
                if len(entityLayer[r][c]) == 1:
                    idx = 0
                else:
                    idx = max(range(len(entityLayer[r][c])),
                            key=lambda i:entityLayer[r][c][i].layer)
                # add character
                self.ScreenBuffer[rw][cl] = entityLayer[r][c][idx].glyph
                if (r < len(self.ColorBuffer)-1 and 
                        c < len(self.ColorBuffer[r])-1):
                    # add color
                    self.ColorBuffer[rw][cl] = entityLayer[r][c][idx].color
    
    def processEvent(self, event):
        '''
        Process key press event from engine, returns energy amount
        '''
        # disregard empty events
        if not event:
            return 0
        if event == chr(ascii.ESC) or event == 'q':
            # QUIT
            self.running = False
            return 0
        elif event == 'r':
            # RESET
            self.MenuManager.State = GameState.PLAYING
            self.gameSetup()
        elif event == ' ':
            # DO NOTHING
            return 1
        elif self.MenuManager.State == GameState.PLAYING:
            # PLAYER ACTION
            # update turn counter
            self.MenuManager.TurnMenu.update()
            self.LevelManager.Player.doAction(event,
                self.LevelManager.getCurrentLevel().EntityLayer)
            return 1
        return 0