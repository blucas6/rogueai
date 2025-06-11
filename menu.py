from enum import Enum
from logger import Logger
from component import Inventory
from message import Messager

class Menu:
    '''
    Basic class to display an updating menu
    Update the text attribute to have it display to the screen at the origin
    Needs a max length in order to clear the menu
    '''
    def __init__(self, screenBuffer: list, origin: tuple,
                 rows: int, cols: int):
        self.origin = origin
        '''Top left corner in screen buffer'''
        self.rows = rows
        '''Max rows for the menu'''
        self.cols = cols
        '''Max cols for the menu'''
        self.text = [' '*self.cols for _ in range(self.rows)]
        '''Text array to be displayed'''
        self.Logger = Logger()
        if (self.origin[0] + self.rows > len(screenBuffer) or
            self.origin[1] + self.cols > len(screenBuffer[0])):
            self.Logger.log(f'Error: {self.__class__.__name__} too big for screen')
        self.update()
    
    def update(self, *args):
        self.text = [' '*self.cols for _ in range(self.rows)]
    
    def display(self, screenBuffer):
        '''
        Adds the current text to the screen buffer
        '''
        for r in range(self.rows):
            for c in range(self.cols):
                rw = r+self.origin[0]
                cl = c+self.origin[1]
                if rw < len(screenBuffer) and cl < len(screenBuffer[rw]):
                    screenBuffer[rw][cl] = ' '
        for r,row in enumerate(self.text):
            for c,ch in enumerate(row):
                rw = r+self.origin[0]
                cl = c+self.origin[1]
                if rw < len(screenBuffer) and cl < len(screenBuffer[rw]):
                    screenBuffer[rw][cl] = ch

class TurnMenu(Menu):
    '''Displays the turn information'''
    def __init__(self, screenBuffer: list, origin: tuple):
        self.count = -1
        '''Turn count'''
        super().__init__(screenBuffer, origin, rows=1, cols=10)

    def update(self):
        '''Updates the turn count'''
        super().update()
        self.count += 1
        self.text[0] = f'Turn: {self.count}'

class DepthMenu(Menu):
    '''Displays the level depth information'''
    def __init__(self, screenBuffer: list, origin: tuple):
        super().__init__(screenBuffer, origin, rows=1, cols=20)
    
    def update(self, z=0):
        '''Updates the level index'''
        super().update()
        self.text[0] = f'Current Level: {z+1}'

class MessageMenu(Menu):
    '''Reads the messager object for messages'''
    def __init__(self, screenBuffer: list, origin: tuple):
        self.Messager = Messager()
        self.msg = ''
        '''Connection to msg queue'''
        super().__init__(screenBuffer, origin, rows=1, cols=50)

    def update(self, blocking=True):
        '''if no msg is being displayed, grab the next msg'''
        super().update()
        if not self.msg:
            self.msg = self.Messager.popMessage(blocking)
            self.text[0] = self.msg
            if self.Messager.MsgQueue:
                self.text[0] += " --more--"
        # self.Logger.log(f'Mesager {self.text}')

    def clear(self):
        '''clears the current msg to allow grabbing a new one'''
        self.msg = ''

class HealthMenu(Menu):
    '''Displays the player health'''
    def __init__(self, screenBuffer: list, origin: tuple):
        self.HealthBarLength = 20
        super().__init__(screenBuffer,
                         origin, rows=1, cols=self.HealthBarLength+2)

    def update(self, health=10, maxhealth=10):
        super().update()
        if health < 0:
            health = 0
        amount = round((self.HealthBarLength * health / maxhealth))
        self.text[0] = '['+amount*'\u2588'+(self.HealthBarLength-amount)*' '+']'

class InventoryMenu(Menu):
    def __init__(self, screenBuffer: list, origin: tuple):
        self.count = 96
        super().__init__(screenBuffer, origin, rows=20, cols=30)
    
    def update(self, inventory: Inventory=None):
        super().update()
        self.text[0] = '=Inventory='
        if inventory:
            self.text[1] = f'(Q)uiver:'
            if inventory.quiver:
                self.text[2] = ' '+inventory.quiver.name
            self.text[3] = f'(M)ain Hand: '
            if inventory.mainHand:
                self.text[4] = ' '+inventory.mainHand.name
            self.text[5] = f'(O)ff Hand: '
            if inventory.offHand:
                self.text[6] = ' '+inventory.offHand.name
            self.text[7] = f'(H)ead: '
            if inventory.head:
                self.text[8] = ' '+inventory.head.name
            self.text[9] = f'(B)ody: '
            if inventory.body:
                self.text[10] = ' '+inventory.body.name
            self.text[11] = f'(F)eet: '
            if inventory.feet:
                self.text[12] = ' '+inventory.feet.name
            self.text[13] = 'Bag:'
            if inventory.contents:
                for idx, entity in enumerate(inventory.contents):
                    i = 14+idx
                    if i < self.rows:
                        self.text[i] = f' ({self.letter()}): {entity.name}'
        self.count = 96

    def letter(self):
        self.count += 1
        return chr(self.count)

class GameState(Enum):
    '''
    Game States:
        1: User inputting actions to the player
        2: Game is over (winning/losing)
        3: Pausing will block player actions
        4: Motion will block player actions until the second event arrives
        5: Running will update the game without user interactions
    '''
    PLAYING = 1
    END = 2
    PAUSEONMSG = 3
    MOTION = 4
    RUNNING = 5

class MenuManager:
    '''
    Handles updating and displaying of game menus
    '''
    def __init__(self, screenBuffer: list):
        '''Sets up all menus'''
        self.TurnMenu = TurnMenu(screenBuffer, (20,0))
        self.DepthMenu = DepthMenu(screenBuffer, (20,10))
        self.MessageMenu = MessageMenu(screenBuffer, (0,0))
        self.HealthMenu = HealthMenu(screenBuffer, (21,0))
        self.InventoryMenu = InventoryMenu(screenBuffer, (1,50))

    def display(self, screenBuffer):
        '''Displays all menus to screen buffer'''
        self.TurnMenu.display(screenBuffer)
        self.DepthMenu.display(screenBuffer)
        self.MessageMenu.display(screenBuffer)
        self.HealthMenu.display(screenBuffer)
        self.InventoryMenu.display(screenBuffer)
