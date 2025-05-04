from game import Game
import curses

class Environment:
    def __init__(self, seed=None, display=True):
        '''
        Initializes the environment
        '''
        self.Game = Game()
        '''game object'''
        self.TimeDelay = 100
        '''max amount of time to wait between bot actions'''
        self.Time = self.TimeDelay
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
            self.Time -= 1
            if self.Time <= 0:
                self.Time = self.TimeDelay
                # decide actions here
            if self.Display and not action:
                # user can command the environment if display is on
                action = self.Game.Engine.readInput()
                if action == 'r':
                    self.reset()
            self.step(action)

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