from enum import Enum

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
        self.MsgQueue = []

    def addMessage(self, msg: str):
        self.MsgQueue.append(msg)

    def popMessage(self, blocking=True):
        if self.MsgQueue:
            if blocking:
                msg = self.MsgQueue[0]
                del self.MsgQueue[0]
            else:
                msg = self.MsgQueue[-1]
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
            for c,ch in enumerate(self.text):
                rw = self.origin[0]
                cl = c+self.origin[1]
                screenBuffer[rw][cl] = ch
            self.textSave = self.text

class TurnMenu(Menu):
    '''Displays the turn information'''
    def __init__(self, origin: tuple, length: int):
        self.count = -1
        super().__init__(origin, length)

    def update(self):
        self.count += 1
        self.text = f'Turn: {self.count}'
        super().update()

class DepthMenu(Menu):
    '''Displays the level depth information'''
    def __init__(self, origin: tuple, length: int):
        super().__init__(origin, length)
    
    def update(self, z=0):
        self.text = f'Current Level: {z+1}'
        super().update()

class MessageMenu(Menu):
    '''Reads the messager object for messages'''
    def __init__(self, origin: tuple, length: int):
        self.Messager = Messager()
        super().__init__(origin, length)

    def update(self, blocking=True):
        self.text = self.Messager.popMessage(blocking)
        if self.Messager.MsgQueue:
            self.text += " --more--"
        super().update()

class GameState(Enum):
    PLAYING = 1
    WON = 2
    PAUSEONMSG = 3

class MenuManager:
    '''
    Handles updating and displaying of game menus
    '''
    def __init__(self):
        self.State = GameState.PLAYING
        self.TurnMenu = TurnMenu((20,0), 10)
        self.DepthMenu = DepthMenu((20,10), 20)
        self.MessageMenu = MessageMenu((0,0), 50)

    def display(self, screenBuffer):
        self.TurnMenu.display(screenBuffer)
        self.DepthMenu.display(screenBuffer)
        self.MessageMenu.display(screenBuffer)
