

class Menu:
    '''
    Basic class to display an updating menu
    '''
    def __init__(self, origin: tuple, length: int):
        self.origin = origin
        '''top left corner in screen buffer'''
        self.text = ''
        self.length = length
        self.textSave = ''
        self.update()

    def update(self, *args, **kwargs):
        self.text += ' '*(self.length-len(self.text))
    
    def display(self, screenBuffer):
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

class WinMenu(Menu):
    '''Displays the state of the game'''
    def __init__(self, origin: tuple, length: int):
        super().__init__(origin, length)
    
    def update(self, win=False):
        if win:
            self.text = 'Game won!'
        super().update()

class MenuManager:
    '''
    Handles updating and displaying of game menus
    '''
    def __init__(self):
        self.TurnMenu = TurnMenu((0,0), 10)
        self.DepthMenu = DepthMenu((0,10), 20)
        self.WinMenu = WinMenu((0,30), 10)

    def display(self, screenBuffer):
        self.TurnMenu.display(screenBuffer)
        self.DepthMenu.display(screenBuffer)
        self.WinMenu.display(screenBuffer)