from logger import Logger
import math
from enum import Enum
from algo import RecursiveShadow
from message import Messager
import copy

ONE_LAYER_CIRCLE = [(1,-1),(1,0),(1,1),(0,-1),(0,0),(0,1),(-1,-1),(-1,0),(-1,1)]

def getOneLayerPts(myPos):
    '''
    Utility function
    Pass in a position to return all points around that position
    '''
    return [[myPos[0]+pt[0],myPos[1]+pt[1]] for pt in ONE_LAYER_CIRCLE]

class PickUp:
    '''
    Pick Up component, an entity will be automatically picked up upon walking
    over it
    '''
    def __init__(self):
        pass

class Charge:
    '''
    Charge component, if an entity can run and charge
    '''
    def __init__(self, speed):
        self.charging = False
        '''If entity is currently charging'''
        self.distance = 0
        '''Distance covered by charge - for damage'''
        self.frameSpeed = 0.005
        '''How much time the engine sleeps during charge'''
        self.entitySpeed = speed
        '''Keeps track of entity speed'''
        self.cost = speed-1
        '''Energy cost for charging move'''

    def start(self, direction: int):
        '''Start the charge, sets direction'''
        self.charging = True
        self.direction = direction
    
    def end(self):
        '''Ends the charge, returns how much damage was dealt'''
        dmg = self.distance
        self.__init__(self.entitySpeed)
        return dmg

class Activate:
    '''
    Activate component, if an entity does something upon a trigger
    '''
    def __init__(self, startingState):
        self.active = startingState
        '''State of the entity'''

    def trigger(self):
        '''Flip the state'''
        self.active = not self.active

class Brain:
    '''
    Brain component, if an entity needs to make decisions
    '''
    def __init__(self, sightRange, blockingLayer):
        self.sightRange = sightRange
        '''How far FOV will check'''
        self.blockingLayer = blockingLayer
        '''Highest level (exclusive) FOV will see through'''

    def input(self, myPos, myZ, playerPos, playerZ, entityLayer):
        '''Returns an action'''
        if playerZ == myZ:
            # only follow if player is on the same level
            pts = self.getFOVFromEntityLayer(entityLayer, myPos)
            if tuple(playerPos) in pts:
                return self.moveTowardsPoint(myPos, playerPos)
        return '.'
    
    def moveTowardsPoint(self, myPos, otherPos):
        '''Moves towards a point on the map'''
        if otherPos[0] > myPos[0]:
            if otherPos[1] > myPos[1]:
                return '3'
            elif otherPos[1] < myPos[1]:
                return '1'
            else:
                return '2'
        elif otherPos[0] < myPos[0]:
            if otherPos[1] > myPos[1]:
                return '9'
            elif otherPos[1] < myPos[1]:
                return '7'
            else:
                return '8'
        else:
            if otherPos[1] > myPos[1]:
                return '6'
            elif otherPos[1] < myPos[1]:
                return '4'
        return '.'
    
    def getFOVFromEntityLayer(self, entityLayer, currPos):
        '''Use FOV algorithm to get which points are visible'''
        grid = [[max([int(x.layer) for x in entityLayer[r][c]])
                 for c in range(len(entityLayer[r]))]
                    for r in range(len(entityLayer))]
        return RecursiveShadow(grid,
                               currPos,
                               self.sightRange,
                               int(self.blockingLayer))

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
    
class Alignment(Enum):
    '''
    Attack components have an alignment, so that creatures of the same
    alignment cannot damage each other
    '''
    LAWFUL = 0
    CHAOTIC = 1

class Wear(Enum):
    HEAD = 0
    BODY = 1
    FEET = 2

class Inventory:
    '''
    Inventory component
    '''
    def __init__(self):
        self.quiver = None
        '''Item in quiver'''
        self.mainHand = None
        '''Item in main hand'''
        self.offHand = None
        '''Item in off hand'''
        self.head = None
        '''Item on head'''
        self.body = None
        '''Item on body'''
        self.feet = None
        '''Item on feet'''
        self.contents = []
        '''Contents of bag'''
        self.maxContents = 10
        '''Max amount of items in bag'''
        self.cost = 1
        '''Cost of using the inventory'''

    def show(self):
        '''Print the inventory to logger'''
        self.Logger = Logger()
        self.Logger.log('Inventory')
        self.Logger.log(f' Quiver: {self.quiver}')
        self.Logger.log(f' Main Hand: {self.mainHand}')
        self.Logger.log(f' Off Hand: {self.offHand}')
        self.Logger.log(f' Head: {self.head}')
        self.Logger.log(f' Body: {self.body}')
        self.Logger.log(f' Feet: {self.feet}')
        self.Logger.log(f' Bag:')
        for e in self.contents:
            self.Logger.log(f'  {e.name}')
    
    def getEntityFromKey(self, char):
        '''
        For a certain character, return the item in the inventory
        
        Will return None in some cases
        '''
        entity = None
        try:
            if char == 'Q':
                entity = copy.deepcopy(self.quiver)
                self.quiver = None
            elif char == 'M':
                entity = copy.deepcopy(self.mainHand)
                self.mainHand = None
            elif char == 'O':
                entity = copy.deepcopy(self.offHand)
                self.offHand = None
            elif char == 'H':
                entity = copy.deepcopy(self.head)
                self.head = None
            elif char == 'B':
                entity = copy.deepcopy(self.body)
                self.body = None
            elif char == 'F':
                entity = copy.deepcopy(self.feet)
                self.feet = None
            else:
                key = ord(char) - 97
                self.Logger.log(f'Inventory key: {key} {char}')
                if key < len(self.contents):
                    entity = copy.deepcopy(self.contents[key])
                    del self.contents[key]
                else:
                    raise
        except Exception as e:
            Messager().addMessage('Invalid inventory key!')
        return entity

    def equip(self, entity):
        '''Pass in an entity to place it in the correct slot'''
        # QUIVER
        if hasattr(self, 'Quiver'):
            if self.quiver:
                if self.quiver.name != entity.name:
                    self.contents.append(copy.deepcopy(self.quiver))
                self.quiver = copy.deepcopy(entity)
        # WEARABLE
        elif hasattr(self, 'Wear'):
            if entity.Wear == Wear.HEAD:
                if self.head:
                    self.contents.append(copy.deepcopy(self.head))
                self.head = copy.deepcopy(entity)
            elif entity.Wear == Wear.BODY:
                if self.body:
                    self.contents.append(copy.deepcopy(self.body))
                self.body = copy.deepcopy(entity)
            elif entity.Wear == Wear.FEET:
                if self.feet:
                    self.contents.append(copy.deepcopy(self.feet))
                self.feet = copy.deepcopy(entity)
        # MAIN / OFF HAND
        else:
            if self.offHand:
                self.contents.append(copy.deepcopy(self.offHand))
            if self.mainHand:
                self.offHand = copy.deepcopy(self.mainHand)
            self.mainHand = copy.deepcopy(entity)
    
    def unequip(self, entity):
        '''
        Pass in an entity to set the corresponding slot to empty and place
        the entity into the bag
        '''
        if self.quiver and self.quiver.id == entity.id:
            self.quiver = None
        elif self.head and self.head.id == entity.id:
            self.head = None
        elif self.body and self.body.id == entity.id:
            self.body = None
        elif self.feet and self.feet.id == entity.id:
            self.feet = None
        elif self.mainHand and self.mainHand.id == entity.id:
            self.mainHand = None
        elif self.offHand and self.offHand.id == entity.id:
            self.offHand = None
        self.contents.append(copy.deepcopy(entity))

    def dealDamage(self):
        '''Based on the slot information calculate the damage'''
        damage = 0
        if self.mainHand and hasattr(self.mainHand, 'Attack'):
            damage += self.mainHand.Attack.damage
        if self.offHand and hasattr(self.offHand, 'Attack'):
            damage += self.offHand.Attack.damage
        return damage
    
    def pickUp(self, entity):
        '''Pass in an entity to add it to the bag'''
        self.contents.append(copy.deepcopy(entity))

    def drop(self):
        '''Place an entity to the ground'''
        pass

class Attack:
    '''
    Attack component, if an entity can be used as an attack
    '''
    def __init__(self, name, damage):
        self.name = name
        '''name of the attack'''
        self.damage = damage
        '''amount of damage the attack does'''