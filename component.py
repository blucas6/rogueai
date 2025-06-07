from logger import Logger
import math
from enum import Enum
from algo import RecursiveShadow

ONE_LAYER_CIRCLE = [(1,-1),(1,0),(1,1),(0,-1),(0,0),(0,1),(-1,-1),(-1,0),(-1,1)]

def getOneLayerPts(myPos):
    '''
    Utility function
    Pass in a position to return all points around that position
    '''
    return [[myPos[0]+pt[0],myPos[1]+pt[1]] for pt in ONE_LAYER_CIRCLE]

class Charge:
    '''
    Charge component, if an entity can run and charge
    '''
    def __init__(self):
        self.charging = False
        '''If entity is currently charging'''
        self.distance = 0
        '''Distance covered by charge - for damage'''
        self.frameSpeed = 0.005
        '''How much time the engine sleeps during charge'''

    def start(self, direction: int):
        '''Start the charge, sets direction'''
        self.charging = True
        self.direction = direction
    
    def end(self):
        '''Ends the charge, returns how much damage was dealt'''
        dmg = self.distance
        self.__init__()
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
        return '5'
    
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
        return '5'
    
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
    LAWFUL = 0,
    CHAOTIC = 1

class Attack:
    '''
    Attack component, if an entity can deal damage
    '''
    def __init__(self, name, damage, alignment: Alignment):
        self.name = name
        '''name of the attack'''
        self.damage = damage
        '''amount of damage the attack does'''
        self.alignment = alignment
        '''prevents attacking the same alignment'''