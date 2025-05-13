from colors import Colors
from logger import Logger
from menu import Messager

class Entity:
    '''
    Base entity class for all objects
    '''
    def __init__(self, name, glyph, color, layer):
        self.name = name
        '''name of entity'''
        self.glyph = glyph
        '''glyph for display'''
        self.color = color
        '''color for display'''
        self.pos = [-1,-1]
        '''starting position is always off map'''
        self.layer = layer
        '''layer for movement'''
        self.z = -1
        '''current z level'''
        self.Messager = Messager()
        '''connection to message queue'''
        self.Logger = Logger()

    def setPosition(self, pos: list, zlevel: int):
        '''
        Sets the position of the entity
        '''
        self.pos = pos
        self.z = zlevel

    def move(self, delta: tuple, entityLayer: list):
        '''
        Moves the entity by a certain delta, checks the layers for validity
        '''
        row = self.pos[0] + delta[0]
        col = self.pos[1] + delta[1]
        maxLayer = max([x.layer for x in entityLayer[row][col]])
        if self.layer > maxLayer:
            self.pos[0] = row
            self.pos[1] = col

    def update(self, entityLayer):
        '''update entity'''
        pass

    def activate(self, *args, **kwargs):
        '''activate an entity property'''
        pass

    def stair(self, entity):
        pass

    def movement(self, key, entityLayer):
        moves = [(1,-1),(1,0),(1,1),(0,-1),(0,0),(0,1),(-1,-1),(-1,0),(-1,1)]
        self.move(moves[key-1], entityLayer)
    
    def moveZ(self, event, entityLayer):
        for entity in entityLayer[self.pos[0]][self.pos[1]]:
            if entity.name == 'Upstair' and event == '<':
                self.Messager.addMessage('You walk up the stairs')
                self.z += 1
                return True
            elif entity.name == 'Downstair' and event == '>':
                self.Messager.addMessage('You walk down the stairs')
                self.z -= 1
                return True
        return False

    def doAction(self, event, entityLayer):
        if event.isdigit():
            self.movement(int(event), entityLayer)
        elif event == '<' or event == '>':
            if not self.moveZ(event, entityLayer):
                self.Messager.addMessage('There are no stairs here')

class Wall(Entity):
    def __init__(self):
        super().__init__('Wall', '0', Colors().white, 2)

class Floor(Entity):
    def __init__(self):
        super().__init__('Floor', '.', Colors().white, 0)

class StairUp(Entity):
    def __init__(self):
        super().__init__('Upstair', '<', Colors().white, 0)

class StairDown(Entity):
    def __init__(self):
        super().__init__('Downstair', '>', Colors().white, 0)