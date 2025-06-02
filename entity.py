from colors import Colors
from logger import Logger
from menu import Messager
import itertools
from component import *
from enum import IntEnum

class Layer(IntEnum):
    '''
    Layer Types:
        0-1: stackable, anything with these layers will be placed on top of
            each other
        2: not stackable, entities that move around, FOV can see through them
        3: not stackable, FOV cannot see through them
    '''
    FLOOR_LAYER = 0,
    OBJECT_LAYER = 1,
    MONST_LAYER = 2,
    WALL_LAYER = 3

class Entity:
    '''
    Base entity class for all objects
    '''
    _id_gen = itertools.count(1)
    '''Shared ID generator'''
    def __init__(self, name, glyph, color, layer):
        self.id = next(Entity._id_gen)
        '''Unique id'''
        self.name = name
        '''Name of entity'''
        self.glyph = glyph
        '''Glyph for display'''
        self.color = color
        '''Color for display'''
        self.pos = [-1,-1]
        '''Starting position is always off map'''
        self.layer = layer
        '''Layer level at which the entity resides'''
        self.z = -1
        '''Current z level'''
        self.Messager = Messager()
        '''Connection to message queue'''
        self.isActive = True
        '''If false, level manager will remove the entity from the game'''
        self.EntityLayerPos = [-1, -1, -1]
        '''Coordinates (xyz) in the Entity Layer, set by level manager'''
        self.turn = 0
        '''Keeps track of game turns'''
        self.Logger = Logger()

    def setPosition(self, pos: list, zlevel: int, idx: int):
        '''
        Sets the position of the entity
        '''
        self.pos = pos
        self.z = zlevel
        self.EntityLayerPos = [pos[0], pos[1], idx]
    
    def remove(self, *args):
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
            # entities that are activated are added to the entity stack
            entities = self.activate(entityLayer)
            return entities
        return []

    def validSpace(self, entityLayer, row, col):
        '''
        Utility for checking in the entity layer
        '''
        if (row < len(entityLayer) and col < len(entityLayer[row]) and
            row >= 0 and col >= 0):
            return True
        return False

    def input(self, *args, **kwargs):
        '''default input entity'''
        return []

    def update(self, *args, **kwargs):
        '''default update entity'''
        return []

    def activate(self, entityLayer):
        '''
        Check for any activatable entities upon entering a square
        '''
        entities = []
        for entity in entityLayer[self.pos[0]][self.pos[1]]:
            if entity is not self and hasattr(entity, 'Activate'):
                entity.Activate.trigger()
                entities.append(entity)
        return entities

    def movement(self, key, entityLayer):
        '''
        Handle the movement action
        '''
        moves = ONE_LAYER_CIRCLE
        row = self.pos[0] + moves[key-1][0]
        col = self.pos[1] + moves[key-1][1]
        self.Logger.log(f'{self.name} m:{(row,col)}')
        if not self.validSpace(entityLayer, row, col):
            return []
        # check if movement triggers an attack
        if not self.attack(entityLayer, row, col):
            # no attack, move normally
            return self.move(row, col, entityLayer)
        return []

    def attack(self, entityLayer, row, col):
        '''
        Check a square and attack it
        Opposing entity must have a Health and it's own Attack
        '''
        for entity in entityLayer[row][col]:
            if (entity is not self and 
                hasattr(entity, 'Health') and
                hasattr(self, 'Attack') and 
                hasattr(entity, 'Attack') and
                entity.Attack.alignment != self.Attack.alignment):
                if entity.Health.changeHealth(-1*self.Attack.damage):
                    self.Messager.addKillMessage(self.name, entity.name)
                    entity.remove(entityLayer)
                else:
                    self.Messager.addDamageMessage(self.name, entity.name)
                # exit if an attack was triggered
                return True
        return False
    
    def moveZ(self, event, entityLayer):
        '''
        Move the entity up or down a level
        '''
        for entity in entityLayer[self.pos[0]][self.pos[1]]:
            if entity.name == 'Upstair' and event == '<':
                self.Messager.addMessage('You walk up the stairs')
                self.z += 1
                return
            elif entity.name == 'Downstair' and event == '>':
                self.Messager.addMessage('You walk down the stairs')
                self.z -= 1
                return
        if event == '<':
            self.Messager.addMessage("Can't go up here")
        elif event == '>':
            self.Messager.addMessage("Can't go down here")

    def doAction(self, event, entityLayer):
        '''
        Entrance for entity actions
        '''
        if event.isdigit():
            return self.movement(int(event), entityLayer)
        elif event == '<' or event == '>':
            self.moveZ(event, entityLayer)
        return []