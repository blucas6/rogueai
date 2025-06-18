import curses
import random
from curses import ascii
from engine import Engine
from level import LevelManager
from color import Colors
from logger import Logger, Timing
from menu import MenuManager, GameState
from message import Messager
import secrets
from enum import Enum

class Event(Enum):
    NA = -1
    CLEAR = 0
    EVENT = 1

class Game:
    '''
    Game class controls the entire game execution from start to finish
    '''
    def __init__(self, specificSeed=None, msgBlocking=True, display=True,
                 timing=False):
        self.Engine = Engine(debug=False)
        '''Connection to engine for displaying and events'''
        self.running = False
        '''If the game is running'''
        self.LevelManager = None
        '''Controls objects in each level'''
        self.ScreenBuffer = None
        '''2D buffer the size of the terminal for outputting to engine'''
        self.ColorBuffer = None
        '''2D buffer the size of the terminal for outputting to engine'''
        self.CreatureLayer = None
        '''2D buffer the size of the map, holds all moving entities'''
        self.MenuManager = None
        '''Holds all information for displaying menus'''
        self.Messager = None
        '''Connection to the message queue instance'''
        self.Energy = 0
        '''Keeps track of how much energy to dispense to objects'''
        self.seed = None
        '''Random seed for random calls'''
        self.MessageBlocking = msgBlocking
        '''Set to true to pause on multiple messages being displayed'''
        self.Display = display
        '''Decides if to set up the game for displaying'''
        self.GameState = GameState.PLAYING
        '''Controls the state of the game'''
        self.playerFOV = True
        '''Use player FOV to generate map'''
        self.specificSeed = specificSeed
        '''Set when recreating a seed'''
        self.previousEvent = ''
        '''Used for key motions of multiple characters'''
        self.Timing = Timing()
        '''Timing for measurements'''
        self.Logger = Logger()
        # turn off logging for timing measurements
        self.Logger.debugOn = not timing
        self.Timing.allowTiming = timing

    def displaySetup(self, stdscr: curses.window, timeDelay: int=None):
        '''
        Sets up the display for outputting to the screen
        '''
        # initialize engine
        self.termRows, self.termCols = self.Engine.init(stdscr, timeDelay)
        self.ScreenBuffer = [[' ' for _ in range(self.termCols-1)] 
                                    for _ in range(self.termRows-1)]
        self.ColorBuffer = [[Colors().white for _ in range(self.termCols-1)] 
                                    for _ in range(self.termRows-1)]

    def noDisplaySetup(self):
        '''
        Sets up the game for not using a display
        '''
        # need to initialize Colors without curses module
        Colors(display=False)
    
    def gameSetup(self):
        '''
        Sets up the game from a fresh start
        '''
        self.Timing.start('Game Setup')
        # start running
        self.running = True
        # set up objects
        if self.specificSeed is None:
            self.seed = secrets.randbits(64)
        else:
            self.seed = self.specificSeed
        self.RNG = random.Random(self.seed)
        self.Logger.log(f'SEED: {self.seed}')
        self.LevelManager = LevelManager(
                                self,
                                self.RNG,
                                height=10,
                                width=20,
                                origin=(4,4),
                                levels=3)
        self.MenuManager = MenuManager(self.ScreenBuffer)
        self.Messager = Messager()
        startPos = [1,1]
        self.LevelManager.defaultLevelSetupWalls(startPos)
        self.LevelManager.addPlayer(pos=startPos, z=0)
        self.LevelManager.Player.update(
            self.LevelManager.getCurrentLevel().EntityLayer
        )
        self.Timing.end()
        # update the game one time (generates FOV)
        self.loop(event='.')

    def start(self, stdscr: curses.window=None):
        '''
        Entry point for the game to start, will call the main loop after
        full initialization
        '''
        if self.Display:
            self.displaySetup(stdscr)
        else:
            self.noDisplaySetup()
        self.gameSetup()
        self.main()
    
    def end(self):
        self.Timing.show()

    def main(self):
        '''
        Main process
        '''
        while self.running:
            # check for events
            event,eventtype = self.processEvents()
            # update the game
            if eventtype == Event.CLEAR:
                self.clearState()
            elif eventtype == Event.EVENT :
                self.loop(event)
            # rewrite all the map buffers and menu buffers to the screen
            self.prepareBuffers()
            # output screen buffer to terminal
            self.render()
        self.end()

    def messages(self):
        '''
        Deal with messages in the queue
        '''
        self.MenuManager.MessageMenu.update(blocking=self.MessageBlocking)
        if self.Messager.MsgQueue:
            # still more messages to process, msg queue should never be full if
            # non blocking mode is on
            self.stateMachine('msgQFull')
        else:
            self.stateMachine('msgQEmpty')
    
    def processEvents(self):
        '''
        Gets an event and it's respective energy (continuously polling)
        '''
        event = self.Engine.readInput()
        if self.GameState != GameState.RUNNING:
            energy,event = self.eventType(event)
        else:
            energy = Event.EVENT
            event = ' '
            self.Engine.pause(self.LevelManager.Player.Charge.frameSpeed)
        return event, energy

    def clearState(self):
        '''Clears the current message'''
        # clear the message queue
        self.MenuManager.MessageMenu.clear()
        # grab new message
        self.messages()
        # update inventory menu
        self.MenuManager.InventoryMenu.update(
            self.LevelManager.Player.Inventory
        )

    def loop(self, event):
        '''
        Execute one loop in the game loop
        '''

        # event was valid, save it
        self.previousEvent = event

        # update the turn
        self.MenuManager.TurnMenu.update()

        # clear current message
        self.MenuManager.MessageMenu.clear()

        # update all entities
        self.LevelManager.updateCurrentLevel(
            event,
            self.MenuManager.TurnMenu.count
        )

        # player has moved to a new level
        if self.LevelManager.swapLevels():
            # update all entities again
            self.LevelManager.updateCurrentLevel(
                event,
                self.MenuManager.TurnMenu.count
            )
            self.LevelManager.Player.clearMentalMap(
                self.LevelManager.getCurrentLevel().EntityLayer)
            # update level menu on level change
            self.MenuManager.DepthMenu.update(self.LevelManager.CurrentZ)

        # update player FOV
        self.LevelManager.setupPlayerFOV()

        # update health menu
        self.MenuManager.HealthMenu.update(
            self.LevelManager.Player.Health.currentHealth,
            self.LevelManager.Player.Health.maxHealth)

        # update inventory menu
        self.MenuManager.InventoryMenu.update(
            self.LevelManager.Player.Inventory
        )

        # check for death
        if not self.GameState == GameState.END and self.lose():
            self.Messager.addMessage('You died!')
            self.stateMachine('endgame')

        # check for win condition
        if not self.GameState == GameState.END and self.win():
            self.Messager.addMessage('You won!')
            self.stateMachine('endgame')

        # check to end the charge
        if not self.LevelManager.Player.Charge.charging:
            self.stateMachine('endrun')

        # update and grab any messages in the queue
        self.messages()

    def render(self):
        '''
        Render the current game state to the screen
        '''
        # display through engine
        if self.Engine.frameReady():
            # output
            self.Engine.output(screenChars=self.ScreenBuffer,
                                screenColors=self.ColorBuffer)

    def prepareBuffers(self):
        '''
        Updates the screen buffer
        '''
        self.LayersToScreen()
        self.MenuManager.display(self.ScreenBuffer)
    
    def win(self):
        '''
        Returns true if the game has been won
        '''
        if self.LevelManager.Player.z == self.LevelManager.TotalLevels-1:
            return True
        return False
    
    def lose(self):
        '''
        Returns if the game is lost
        '''
        if self.LevelManager.Player.Health.alive:
            return False
        return True

    def boundsCheck(self, buffer, r, c):
        '''
        Checks if a position is valid within the screen buffer
        '''
        if (r > len(buffer)-1 or c > len(buffer[r])-1):
            return False
        return True

    def mapPosToScreenPos(self, r, c):
        return r+self.LevelManager.origin[0], c+self.LevelManager.origin[1]
    
    def LayersToScreen(self):
        '''
        Build buffers according to layer information
        '''
        if self.playerFOV:
            entityLayer = self.LevelManager.Player.mentalMap
        else:
            entityLayer = self.LevelManager.getCurrentLevel().EntityLayer
        # go through entity layer
        for r,row in enumerate(entityLayer):
            for c,col in enumerate(row):
                rw, cl = self.mapPosToScreenPos(r,c)
                # find top most entity
                if not entityLayer[r][c]:
                    glyph = self.LevelManager.Player.unknownGlyph
                    color = self.LevelManager.Player.unknownColor
                elif len(entityLayer[r][c]) == 1:
                    glyph = entityLayer[r][c][0].glyph
                    color = entityLayer[r][c][0].color
                else:
                    idx = max(range(len(entityLayer[r][c])),
                            key=lambda i:entityLayer[r][c][i].layer)
                    glyph = entityLayer[r][c][idx].glyph
                    color = entityLayer[r][c][idx].color
                if not self.boundsCheck(self.ScreenBuffer, rw, cl):
                    continue
                # add glyph
                self.ScreenBuffer[rw][cl] = glyph
                if not self.boundsCheck(self.ColorBuffer, rw, cl):
                    continue
                # add color
                self.ColorBuffer[rw][cl] = color
        # go through light layer
        lightLayer = self.LevelManager.getCurrentLevel().LightLayer
        for r,row in enumerate(lightLayer):
            for c,col in enumerate(row):
                rw, cl = self.mapPosToScreenPos(r,c)
                if lightLayer[r][c]:
                    color = Colors().yellow
                    self.ColorBuffer[rw][cl] = color
    
    def eventType(self, event):
        '''
        Process key press event from engine

             -1: does not count as an action

            0 : will not cause an update because turn counter does not increase,
                updates menus

            1+ : counts as a energy for updating entities
        '''
        # disregard empty events
        if not event:
            return Event.NA,event
        if self.GameState == GameState.MOTION:
            self.stateMachine('donemotion')
            # MOTION EVENTS
            if self.previousEvent == 't' or self.previousEvent == '5':
                # Throwing/Charge Action
                # expects a direction
                if not event.isdigit() or event == '5':
                    self.Messager.addMessage('Invalid direction!')
                    return Event.CLEAR,event
                # valid direction increment turn
                # return the combined event
                if self.previousEvent == '5':
                    self.stateMachine('startrun')
                return Event.EVENT,self.previousEvent+event
            elif self.previousEvent == 'e' or self.previousEvent == 'u':
                # Inventory Action
                return Event.EVENT,self.previousEvent+event
        if event == chr(ascii.ESC) or event == 'q':
            # QUIT
            self.running = False
        elif event == 'r':
            # RESET
            self.stateMachine('reset')
            self.gameSetup()
        elif event == 'f':
            # TOGGLE FOV
            self.playerFOV = not self.playerFOV
        elif event == ' ':
            # DO NOTHING - clears msg queue
            return Event.CLEAR,event
        elif ((event == 't' or event == '5') and
              self.GameState == GameState.PLAYING):
            # Multi key action
            self.Messager.addMessage('Direction?')
            self.stateMachine('motion')
            self.previousEvent = event
            return Event.CLEAR,event
        elif ((event == 'e' or event == 'u') and
              self.GameState == GameState.PLAYING):
            # Multi key action
            if event == 'e':
                self.Messager.addMessage('Equip what?')
            elif event == 'u':
                self.Messager.addMessage('Unequip what?')
            self.stateMachine('motion')
            self.previousEvent = event
            return Event.CLEAR,event
        elif self.GameState == GameState.PLAYING:
            # PLAYER ACTION
            return Event.EVENT,event
        # Defaults to returning -1 for no action
        return Event.NA,event

    def stateMachine(self, event):
        '''
        Change the game state
        '''
        if event == 'msgQFull' and self.GameState == GameState.PLAYING:
            # too many messages to display, block user input until resolved
            self.GameState = GameState.PAUSEONMSG
        elif event == 'msgQEmpty' and self.GameState == GameState.PAUSEONMSG:
            # if paused and msg queue is cleared, go back to normal
            self.GameState = GameState.PLAYING
        elif event == 'endgame':
            self.GameState = GameState.END
        elif event == 'reset':
            self.GameState = GameState.PLAYING
        elif event == 'motion' and self.GameState == GameState.PLAYING:
            # start the key motion
            self.GameState = GameState.MOTION
        elif event == 'donemotion' and self.GameState == GameState.MOTION:
            # end the key motion
            self.GameState = GameState.PLAYING
        elif event == 'startrun' and self.GameState == GameState.PLAYING:
            # start the charge
            self.GameState = GameState.RUNNING
        elif event == 'endrun' and self.GameState == GameState.RUNNING:
            # end the charge
            self.GameState = GameState.PLAYING
