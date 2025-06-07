from game import Game
import curses
from geneticBot import GeneticBot, GeneticManager
from menu import GameState

class Environment:
    def __init__(self, seed=None, display=True):
        '''
        Initializes the environment
        '''
        self.Game = Game(
            seed=seed,
            msgBlocking=False
        )
        '''game object'''
        self.ActionDelay = 10
        '''max amount of time to wait between bot actions'''
        self.Delay = self.ActionDelay
        '''current time waiting'''
        self.seedn = seed
        '''seed for the game'''
        self.Display = display
        '''choose to display the game board'''
        self.state_space_shape = None
        self.action_space_shape = None
        self.state = None
        # if using the display, start the curses module
        if self.Display:
            curses.wrapper(self.start)
        else:
            self.start()

    def start(self, stdscr: curses.window=None):
        '''
        Environment start calls the game initialization and runs the 
        environment loop instead of the game loop
        '''
        # initialize the game display if running with display on
        if self.Display:
            self.Game.displaySetup(stdscr)
        else:
            self.Game.noDisplaySetup()
        # setup the game
        self.Game.gameSetup()
        # use the environment main loop instead of the game main loop
        self.main()

    def main(self):
        '''
        Environment game loop
        '''
        while self.Game.running:
            action = None
            self.Delay -= 1
            if self.Delay <= 0:
                self.Delay = self.ActionDelay
                # decide actions here
                #
                #
            if self.Display:
                # user can command the environment if display is on
                event = self.Game.Engine.readInput()
                if event:
                    action = event
            self.step(action)

    def collectGameInfo(self):
        '''collect game information for observations here'''
        turns = self.Game.MenuManager.TurnMenu.count
        score = self.Game.LevelManager.CurrentZ
        won = True if self.Game.MenuManager.State == GameState.END else False
        return turns, score, won

    def reset(self):
        '''
        Resets the environment to an initial state
        '''
        return NotImplementedError

    def step(self, action):
        '''
        Takes one step in the environment
        '''
        self.Game.loop(action)
        self.Game.messages()
        if self.Display:
            self.Game.prepareBuffers()
            self.Game.render()
            self.Game.animations()

    def render(self):
        '''
        (Optional) Renders the environment for visualization
        '''
        pass

    def seed(self, seed=None):
        '''
        (Optional) Sets the seed for reproducibility
        '''
        pass