from color import Colors
from logger import Logger
from message import Messager
import itertools
from component import *
from enum import IntEnum
from algo import *
from animation import *

class AttackSpeed(IntEnum):
    VERY_SLOW = 7
    SLOW = 6
    AVERAGE = 5
    FAST = 4
    VERY_FAST = 3

class Speed(IntEnum):
    VERY_SLOW = 9
    SLOW = 8
    AVERAGE = 7
    FAST = 6
    VERY_FAST = 5

class Layer(IntEnum):
    '''
    Layer Types:
        0-1: stackable, anything with these layers will be placed on top of
            each other
        2: not stackable, entities that move around, FOV can see through them
        3: not stackable, FOV cannot see through them
    '''
    FLOOR_LAYER = 0
    OBJECT_LAYER = 1
    MONST_LAYER = 2
    WALL_LAYER = 3

class Size(IntEnum):
    '''
    Size Types:
        1: very small, like darts
        2: small, like insects
        3: medium, hobbits or kobolds
        4: large, people
        5: very large, orcs or trolls
        6: giant, yep giants
        7: humongous, titans
    '''
    VERY_SMALL = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 4
    VERY_LARGE = 5
    GIANT = 6
    HUMONGOUS = 7

class Entity:
    '''
    Base entity class for all objects
    '''
    _id_gen = itertools.count(1)
    '''Shared ID generator'''
    def __init__(self, name: str, glyph: str, color: Colors, layer: Layer,
                 size: Size):
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
        self.size = size
        '''Size enum for the entity'''
        self.energy = 0
        '''Energy bank'''
        self.tookTurn = False
        '''Flag to check if an entity took a turn'''
        self.setup()

    def setup(self):
        '''Default setup - always called on entity initialization'''
        self.Logger = Logger()

    def setPosition(self, pos: list, zlevel: int, idx: int):
        '''
        Sets the position of the entity
        '''
        self.pos = pos
        self.z = zlevel
        self.EntityLayerPos = [pos[0], pos[1], idx]

    def death(self, *args):
        '''
        Overload to create an on death behavior
        '''
        pass

    def remove(self, *args):
        '''
        Triggers the removal of this entity from the entity layer

        Level Manager will call death function
        '''
        self.isActive = False
    
    def takeTurn(self, cost):
        self.tookTurn = True
        if cost > self.energy:
            self.energy = 0
        else:
            self.energy -= cost
    
    def handleInventory(self, event, entityLayer):
        if hasattr(self, 'Inventory'):
            self.Inventory.show()
            if len(event) > 1 and self.energy >= self.Inventory.cost:
                key = event[1]
                event = event[0]
                if event == 'e':
                    self.takeTurn(self.Inventory.cost)
                    entity = self.Inventory.getEntityFromKey(key)
                    if entity:
                        self.Inventory.equip(entity)
                elif event == 'u':
                    self.takeTurn(self.Inventory.cost)
                    entity = self.Inventory.getEntityFromKey(key)
                    if entity:
                        self.Inventory.unequip(entity)

    def handleCharging(self, state, direction=None, entityLayer=[]):
        '''Checks if an entity can charge and is charging'''
        if hasattr(self, 'Charge'):
            if self.Charge.charging:
                if state == 'trymove':
                    return self.Charge.cost
                if state == 'move':
                    self.Charge.distance += 1
                elif state == 'endmove' or state == 'invalid':
                    self.Charge.end()
                elif state == 'damage':
                    return self.Charge.end()
            elif state == 'start':
                self.Charge.start(int(direction))
                self.movement(self.Charge.direction, entityLayer)

    def move(self, row: int, col: int, entityLayer: list):
        '''
        Moves the entity by a certain delta, checks the layers for validity

        If an entity is charging, it will increment the distance

        If an entity is charging and the position is invalid, it will end the
        charge
        '''
        if hasattr(self, 'speed'):
            maxLayer = max([x.layer for x in entityLayer[row][col]])
            chargeCost = self.handleCharging('trymove')
            if self.layer > maxLayer:
                if not chargeCost:
                    cost = self.speed
                else:
                    cost = chargeCost
                if self.energy >= cost:
                    # move is valid
                    self.pos[0] = row
                    self.pos[1] = col
                    # if charging, count as a move forward
                    self.handleCharging('move')
                    # entities that are activated are added to the entity stack
                    entities = self.activate(entityLayer)
                    self.takeTurn(cost)
                    self.Logger.log(f'energy after a move: {self.energy}')
                    return entities
            else:
                # hit a wall
                if chargeCost and self.energy >= chargeCost:
                    # entity was charging
                    self.takeTurn(chargeCost)
                    # if charging, end the charge
                    self.handleCharging('endmove')
                else:
                    self.takeTurn(self.speed)

    def validBounds(self, entityLayer, row, col):
        '''
        Utility for checking the bounds in the entity layer
        '''
        if (row < len(entityLayer) and col < len(entityLayer[row]) and
            row >= 0 and col >= 0):
            return True
        return False

    def input(self, *args, **kwargs):
        '''Default input entity'''
        self.takeTurn(100)

    def update(self, *args, **kwargs):
        '''
        Default update entity
        
        Update may be called several times per turn
        '''
        pass

    def activate(self, entityLayer):
        '''
        Check for any activatable entities upon entering a square
        '''
        entities = []
        elist = entityLayer[self.pos[0]][self.pos[1]]
        for idx, entity in enumerate(elist):
            # check for an entity that has the activate component
            if entity is not self and hasattr(entity, 'Activate'):
                entity.Activate.trigger()
                entities.append(entity)
            if entity is not self and hasattr(entity, 'PickUp') and hasattr(self, 'Inventory'):
                self.Inventory.pickUp(entity)
                entity.remove()
                entities.append(entity)
        return entities

    def movement(self, key, entityLayer):
        '''
        Handle the movement action

        If charging and movement becomes invalid, end charge
        '''
        # find next position
        moves = ONE_LAYER_CIRCLE
        row = self.pos[0] + moves[key-1][0]
        col = self.pos[1] + moves[key-1][1]
        # check validity
        if not self.validBounds(entityLayer, row, col):
            self.handleCharging('invalid')
            return
        # check if movement triggers an attack
        attack, entities = self.attack(entityLayer, row, col)
        if not attack:
            # no attack, move normally
            return self.move(row, col, entityLayer)
        # attack took place, return the (possibly) killed entity
        return entities

    def attack(self, entityLayer, row, col):
        '''
        Check a square and attack it

        Opposing entity must have a Health and it's own Attack

        Returns True if there was an attack, and the entity that was killed
        '''
        # go through possible entities to attack
        for entity in entityLayer[row][col]:
            # check if you can attack this entity
            if (hasattr(self, 'Inventory') and
                hasattr(self, 'attackSpeed') and self.attackable(entity)):
                chargeDmg = self.handleCharging('damage')
                # if it was currently charging use the charge damage
                if chargeDmg:
                    damage = chargeDmg
                    cost = self.Charge.cost
                    self.Messager.addChargeMessage(self.name, entity.name)
                # otherwise attack normally
                else:
                    cost = self.attackSpeed
                    damage = self.Inventory.dealDamage()
                # check if you have enough energy to attack
                if self.energy >= cost:
                    # send damage to entity
                    kill = self.dealDamage(
                        entityLayer,
                        entity,
                        damage
                    )
                    self.takeTurn(cost)
                    # exit if an attack was triggered
                    if kill:
                        return True, [kill]
                return True, None
        return False, None

    def dealDamage(self, entityLayer, entity, damage, nomsg=False):
        '''
        Deal damage to another entity and possibly kill it

        Damage will be inversed

        Returns the entity if it was killed
        '''
        damage = damage * -1
        self.Logger.log(f'{self.name} dealing {damage} to {entity.name}')
        if entity.Health.changeHealth(damage):
            self.Messager.addKillMessage(self.name, entity.name)
            entity.remove(entityLayer)
            return entity
        elif not nomsg:
            self.Messager.addDamageMessage(self.name, entity.name)
    
    def attackable(self, entity):
        '''Checks if an entity can be attacked'''
        if (entity is not self and 
            hasattr(entity, 'Health')):
            return True
        return False
    
    def moveZ(self, event, entityLayer):
        '''
        Move the entity up or down a level
        '''
        if hasattr(self, 'speed') and self.energy >= self.speed:
            for entity in entityLayer[self.pos[0]][self.pos[1]]:
                if entity.name == 'Upstair' and event == '<':
                    self.Messager.addMessage('You walk up the stairs')
                    self.z += 1
                    self.takeTurn(self.speed)
                    return
                elif entity.name == 'Downstair' and event == '>':
                    self.Messager.addMessage('You walk down the stairs')
                    self.z -= 1
                    self.takeTurn(self.speed)
                    return
            if event == '<':
                self.Messager.addMessage("Can't go up here")
            elif event == '>':
                self.Messager.addMessage("Can't go down here")

    def throw(self, entity, entityLayer, direction=[], target=[]):
        '''
        Base throw method

        Child classes should implement a method that uses the base method and
        passes an entity to be thrown

        If direction is included, the entity will be thrown in that direction
        until it hits a wall layer

        If target is included, the entity will be sent directly to that target's
        position
        '''
        if hasattr(self, 'throwSpeed') and self.energy >= self.throwSpeed:
            self.Logger.log(f'trying to throw')
            if (direction and len(direction) == 2 and
                not (direction[0] == 0 and direction[1] == 0)): 
                # find the final position for the thrown object
                # start object from entity throwing position
                objr, objc = self.pos[0], self.pos[1]
                while True:
                    r,c = objr + direction[0], objc + direction[1]
                    maxLayer = max([x.layer for x in entityLayer[r][c]])
                    if maxLayer == Layer.MONST_LAYER:
                        objr, objc = r, c
                        break
                    elif maxLayer == Layer.WALL_LAYER:
                        break
                    objr, objc = r, c
                entity.setPosition(pos=[objr,objc], zlevel=self.z, idx=-1)
            elif target:
                # set the known position
                entity.setPosition(pos=target, zlevel=self.z, idx=-1)
            else:
                self.Logger.log(f'Error: invalid throw')
                return
            
            # construct a grid of 1,0 (makes sure path to end point is valid)
            grid = [[1 if max([int(x.layer) for x in elist])
                    > Layer.MONST_LAYER else 0
                    for elist in row]
                    for row in entityLayer]
            code, pts = astar(grid, tuple(self.pos), tuple(entity.pos))
            if code != 1:
                self.Logger.log(f'Error: failed to throw -> {code}')
                return

            self.Logger.log('throwing!!')
            # deal damage
            entities = []
            dmg = entity.size * 2
            r,c = entity.pos[0], entity.pos[1]
            for e in entityLayer[r][c]:
                if self.attackable(e):
                    kill = self.dealDamage(entityLayer, e, dmg)
                    if kill:
                        entities.append(kill)

            # create the animation
            frames = {}
            for idx,pt in enumerate(pts):
                frames[str(idx)] = [['' for col in row] for row in grid]
                frames[str(idx)][pt[0]][pt[1]] = entity.glyph
            apos = [0,0]
            delay = 0.05
            animation = Animation(apos, frames, entity.color, delay=delay)
            animator = Animator()
            animator.queueUp(animation)
            # add thrown entity to stack
            entities.append(entity)
            # 
            self.takeTurn(self.throwSpeed)
            return entities

    def doAction(self, event, entityLayer):
        '''
        Entrance for entity actions
        '''
        self.Logger.log(f'Do action [{self.name}|{self.id}]: e:{self.energy} {event}')
        if hasattr(self, 'Charge') and self.Charge.charging:
            # charge action
            # override all other events and keep charging
            return self.movement(self.Charge.direction, entityLayer)
        elif event[0] == '5' and len(event) > 1:
            # start a charge
            return self.handleCharging('start', event[1], entityLayer)
        elif event.isdigit():
            # movement action
            return self.movement(int(event), entityLayer)
        elif event == '<' or event == '>':
            # stair action
            self.moveZ(event, entityLayer)
        elif event[0] == 't':
            # throwing action
            return self.fire(entityLayer, event)
        elif (hasattr(self, 'Inventory') and 
              event[0] == 'e' or event[0] == 'u'):
            # inventory actions
            self.handleInventory(event, entityLayer)
        elif event == '.':
            # resting
            self.takeTurn(100)
        else:
            self.takeTurn(100)