from enum import Enum
from logger import Logger
from component import Inventory

class Messager:
    '''
    Singleton class to write game action messages to
    '''
    _instance = None

    def __new__(obj):
        if not obj._instance:
            obj._instance = super(Messager, obj).__new__(obj)
            obj._instance.clear()
        return obj._instance
    
    def clear(self):
        '''
        Clears the msg queue
        '''
        self.MsgQueue = []

    def addMessage(self, msg: str):
        '''
        Adds a msg to the msg queue
        '''
        self.MsgQueue.append(msg)
    
    def addDamageMessage(self, nameAttack: str, nameDefend: str):
        if nameAttack == 'Player':
            self.MsgQueue.append(f'You hit the {nameDefend}')
        elif nameDefend == 'Player':
            self.MsgQueue.append(f'The {nameAttack} hits you')
        else:
            self.MsgQueue.append(f'The {nameAttack} hits the {nameDefend}')
    
    def addKillMessage(self, nameAttack: str, nameDefend: str):
        if nameAttack == 'Player':
            self.MsgQueue.append(f'You kill the {nameDefend}!')
        elif nameDefend == 'Player':
            self.MsgQueue.append(f'The {nameAttack} kills you!')
        else:
            self.MsgQueue.append(f'The {nameAttack} kills the {nameDefend}!')

    def addChargeMessage(self, nameAttack: str, nameDefend: str):
        if nameAttack == 'Player':
            self.MsgQueue.append(f'You charge the {nameDefend}')
        elif nameDefend == 'Player':
            self.MsgQueue.append(f'The {nameAttack} charges you!')
        else:
            self.MsgQueue.append(f'The {nameAttack} charges the {nameDefend}')

    def popMessage(self, blocking=True):
        '''
        If msg queue has a msg, it will return the msg by FIFO
        '''
        if self.MsgQueue:
            if blocking:
                msg = self.MsgQueue[0]
                del self.MsgQueue[0]
            else:
                msg = self.MsgQueue[0]
                self.MsgQueue = []
            return msg
        return ''

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
        self.mainHandName = ''
        self.offHandName = ''
        self.quiverName = ''
        self.contentsName = ''
        self.count = 96
        super().__init__(origin, length)
    
    def update(self, inventory: Inventory=None):
        super().update()
        if inventory:
            if inventory.quiver:
                self.quiver = f'({self.letter()}): {inventory.quiver.name}'
            if inventory.mainHand:
                self.mainHandName = f'({self.letter()}): {inventory.mainHand.name}'
            if inventory.offHand:
                self.offHandName = f'({self.letter()}): {inventory.offHand.name}'
            if inventory.contents:
                for entity in inventory.contents:
                    self.contentsName += f'  ({self.letter()}): {entity.name}\n'
        self.text = f'=Inventory=\n' \
                    f'Quiver:\n' \
                    f'   {self.quiverName}\n' \
                    f'Main Hand: \n' \
                    f'   {self.mainHandName}\n' \
                    f' Off Hand: \n' \
                    f'   {self.offHandName}\n' \
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
