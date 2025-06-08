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
    def __init__(self, origin: tuple, length: int):
        self.origin = origin
        '''top left corner in screen buffer'''
        self.text = ''
        '''text string to be displayed'''
        self.length = length
        '''max length for the text string'''
        self.textSave = ''
        '''previously used text message'''
        self.Logger = Logger()
        self.update()

    def update(self, *args, **kwargs):
        '''
        Child classes should always call base update to fully clear out previous
        text messages
        '''
        self.text += ' '*(self.length-len(self.text))
    
    def display(self, screenBuffer):
        '''
        Adds the current text to the screen buffer
        '''
        if self.textSave != self.text:
            r = 0
            c = 0
            for ch in self.text:
                c += 1
                if ch == '\n':
                    r += 1
                    c = 0
                rw = r+self.origin[0]
                cl = c+self.origin[1]
                screenBuffer[rw][cl] = ch
            self.textSave = self.text

class TurnMenu(Menu):
    '''Displays the turn information'''
    def __init__(self, origin: tuple, length: int):
        self.count = -1
        '''turn count'''
        super().__init__(origin, length)

    def update(self):
        '''updates the turn count'''
        self.count += 1
        self.text = f'Turn: {self.count}'
        super().update()

class DepthMenu(Menu):
    '''Displays the level depth information'''
    def __init__(self, origin: tuple, length: int):
        super().__init__(origin, length)
    
    def update(self, z=0):
        '''updates the level index'''
        self.text = f'Current Level: {z+1}'
        super().update()

class MessageMenu(Menu):
    '''Reads the messager object for messages'''
    def __init__(self, origin: tuple, length: int):
        self.Messager = Messager()
        '''connection to msg queue'''
        super().__init__(origin, length)

    def update(self, blocking=True):
        '''if no msg is being displayed, grab the next msg'''
        if not self.text:
            self.text = self.Messager.popMessage(blocking)
            if self.Messager.MsgQueue:
                self.text += " --more--"
        super().update()

    def clear(self):
        '''clears the current msg to allow grabbing a new one'''
        self.text = ''

class HealthMenu(Menu):
    '''Displays the player health'''
    def __init__(self, origin: tuple, length: tuple):
        self.HealthBarLength = length-2
        super().__init__(origin, length)

    def update(self, health=10, maxhealth=10):
        if health < 0:
            health = 0
        amount = round((self.HealthBarLength * health / maxhealth))
        self.text = '['+amount*'\u2588'+(self.HealthBarLength-amount)*' '+']'

class InventoryMenu(Menu):
    def __init__(self, origin: tuple, length: tuple):
        self.quiverName = ''
        self.mainHandName = ''
        self.offHandName = ''
        self.headName = ''
        self.bodyName = ''
        self.feetName = ''
        self.contentsName = ''
        self.count = 96
        super().__init__(origin, length)
    
    def update(self, inventory: Inventory=None):
        super().update()
        if inventory:
            self.quiverName = f'({self.letter()}) Quiver:\n  '
            if inventory.quiver:
                self.quiverName += inventory.quiver.name
            self.mainHandName = f'({self.letter()}) Main Hand:\n  '
            if inventory.mainHand:
                self.mainHandName += inventory.mainHand.name
            self.offHandName = f'({self.letter()}) Off Hand:\n  '
            if inventory.offHand:
                self.offHandName += inventory.offHand.name
            self.headName = f'({self.letter()}) Head:\n  '
            if inventory.head:
                self.headName += inventory.head.name
            self.bodyName = f'({self.letter()}) Body:\n  '
            if inventory.body:
                self.bodyName += inventory.body.name
            self.feetName = f'({self.letter()}) Feet:\n  '
            if inventory.feet:
                self.feetName += inventory.feet.name
            self.contentsName = ''
            if inventory.contents:
                self.Logger.log(f'MY menu inventory {inventory.contents}')
                for entity in inventory.contents:
                    self.contentsName += f' ({self.letter()}): {entity.name}\n'
        self.text = f'=Inventory=\n' \
                    f'{self.quiverName}\n' \
                    f'{self.mainHandName}\n' \
                    f'{self.offHandName}\n' \
                    f'\n' \
                    f'Bag:\n'
        self.text += self.contentsName

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
    def __init__(self):
        '''Sets up all menus'''
        self.TurnMenu = TurnMenu((20,0), 10)
        self.DepthMenu = DepthMenu((20,10), 20)
        self.MessageMenu = MessageMenu((0,0), 50)
        self.HealthMenu = HealthMenu((21,0), 20)
        self.InventoryMenu = InventoryMenu((1,50), 100)

    def display(self, screenBuffer):
        '''Displays all menus to screen buffer'''
        self.TurnMenu.display(screenBuffer)
        self.DepthMenu.display(screenBuffer)
        self.MessageMenu.display(screenBuffer)
        self.HealthMenu.display(screenBuffer)
        self.InventoryMenu.display(screenBuffer)
