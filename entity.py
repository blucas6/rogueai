from colors import Colors
from logger import Logger
from menu import Messager

ONE_LAYER_CIRCLE = [(1,-1),(1,0),(1,1),(0,-1),(0,0),(0,1),(-1,-1),(-1,0),(-1,1)]

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
        self.isActive = True
        '''if false, level manager will remove the entity from the game'''
        self.Logger = Logger()

    def setPosition(self, pos: list, zlevel: int):
        '''
        Sets the position of the entity
        '''
        self.pos = pos
        self.z = zlevel
    
    def remove(self, entityLayer):
        '''
        Triggers the removal of this entity from the entity layer
        '''
        self.isActive = False

    def move(self, row: int, col: int, entityLayer: list):
        '''
        Moves the entity by a certain delta, checks the layers for validity
        '''
        maxLayer = max([x.layer for x in entityLayer[row][col]])
        if self.layer > maxLayer:
            self.pos[0] = row
            self.pos[1] = col

    def validSpace(self, entityLayer, row, col):
        '''
        Utility for checking in the entity layer
        '''
        if (row < len(entityLayer) and col < len(entityLayer[row]) and
            row >= 0 and col >= 0):
            return True
        return False

    def update(self, entityLayer):
        '''default update entity'''
        pass

    def activate(self, *args, **kwargs):
        '''activate an entity property'''
        pass

    def movement(self, key, entityLayer):
        '''
        Handle the movement action
        '''
        moves = ONE_LAYER_CIRCLE
        row = self.pos[0] + moves[key-1][0]
        col = self.pos[1] + moves[key-1][1]
        if not self.validSpace(entityLayer, row, col):
            return
        # check if movement triggers an attack
        for entity in entityLayer[row][col]:
            if hasattr(entity, 'Health') and hasattr(self, 'Attack'):
                if entity.Health.changeHealth(-1*self.Attack.damage):
                    self.Messager.addMessage(f'You kill the {entity.name}!')
                    entity.remove(entityLayer)
                else:
                    self.Messager.addMessage(f'You hit the {entity.name}')
                return
        # no attack, move normally
        self.move(row, col, entityLayer)
    
    def moveZ(self, event, entityLayer):
        '''
        Move the entity up or down a level
        '''
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
        '''
        Entrance for entity actions
        '''
        if event.isdigit():
            self.movement(int(event), entityLayer)
        elif event == '<' or event == '>':
            if not self.moveZ(event, entityLayer):
                self.Messager.addMessage('There are no stairs here')

class Health:
    '''
    Health component, if an entity needs a health bar
    '''
    def __init__(self, health):
        self.maxHealth = health
        '''Maximum for the health bar'''
        self.currentHealth = health
        '''Counter for current health'''
        self.alive = True
        '''True if health bar is above 0'''
        self.Logger = Logger()

    def changeHealth(self, amount):
        '''
        Changes the health bar by an amount
        Returns true if health change causes death
        '''
        self.currentHealth += amount
        if self.alive and self.currentHealth <= 0:
            self.alive = False
            return True
        return False

class Attack:
    '''
    Attack component, if an entity can deal damage
    '''
    def __init__(self, name, damage):
        self.name = name
        '''name of the attack'''
        self.damage = damage
        '''amount of damage the attack does'''

class Wall(Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__('Wall', '░', Colors().white, 2)

class Floor(Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__('Floor', '.', Colors().white, 0)

class StairUp(Entity):
    '''Up stair entity'''
    def __init__(self):
        super().__init__('Upstair', '<', Colors().white, 0)

class StairDown(Entity):
    '''Down stair entity'''
    def __init__(self):
        super().__init__('Downstair', '>', Colors().white, 0)