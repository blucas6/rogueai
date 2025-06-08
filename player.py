from entity import *
from component import *
from color import Colors
from tower import *
from enum import Enum
from item import *
import copy

class FOVMemory(Enum):
    '''
    Types of FOV Memory:
        0: remember nothing
        1: remember only the object layer
        2: remember everything
    '''
    NOTHING = 0,
    OBJECTS = 1,
    EVERYTHING = 2

class Player(Entity):
    def __init__(self, rows, cols):
        self.Health = Health(health=6)
        '''Health component'''
        self.mentalMap = [[[] for _ in range(cols)] for _ in range(rows)]
        '''Entity map for output to the screen'''
        self.fovPoints = ONE_LAYER_CIRCLE
        '''Used for simple FOV'''
        self.fovMemory = FOVMemory.OBJECTS
        '''Decides the type of FOV the player gets'''
        self.sightRange = 4
        '''How far the FOV will check'''
        self.unknownGlyph = ' '
        '''Glyph to show unexplored territory'''
        self.unknownColor = Colors().white
        '''Color of glyph for unexplored territory'''
        self.blockingLayer = Layer.MONST_LAYER
        '''For FOV, highest level (exclusive) to see through'''
        self.Brain = Brain(self.sightRange, self.blockingLayer)
        '''Player brain for game interactions'''
        self.Charge = Charge()
        '''Player can run'''
        self.Inventory = Inventory()
        ''''''
        super().__init__(name='Player',
                         glyph='@',
                         color=Colors().white,
                         layer=Layer.MONST_LAYER,
                         size=Size.LARGE)

    def setup(self):
        super().setup()
        # self.Inventory.equip(Sword())
        self.Inventory.contents.append(Sword())
    
    def handleInventoryAction(self, event, key):
        self.Inventory.show()
        if event == 'e':
            entity = self.Inventory.getEntityFromKey(key)
            if entity:
                self.Inventory.equip(entity)

    def input(self, energy, entityLayer, playerPos, playerZ, event):
        '''
        Receives the player event and uses it
        '''
        self.Logger.log(f'Player event: {event}')
        return self.doAction(event, entityLayer)

    def setupFOV(self, entityLayer, lightLayer):
        '''Get the FOV for the player'''
        # pts = self.getSimpleFOV()
        pts = self.Brain.getFOVFromEntityLayer(entityLayer, self.pos)
        if self.fovMemory == FOVMemory.NOTHING:
            # always clear previous points
            self.mentalMap = [[[] for _ in range(len(entityLayer[row]))]
                                    for row in range(len(entityLayer))]
        if self.fovMemory == FOVMemory.EVERYTHING:
            # just add new seen points
            for pt in pts:
                self.mentalMap[pt[0]][pt[1]] = copy.deepcopy(
                                                    entityLayer[pt[0]][pt[1]]
                                                    )
        elif self.fovMemory == FOVMemory.OBJECTS:
            for r,row in enumerate(entityLayer):
                for c,col in enumerate(row):
                    if (r,c) in pts:
                        self.mentalMap[r][c] = copy.deepcopy(entityLayer[r][c])
                    elif self.mentalMap[r][c]:
                        # seen before, but not in current FOV
                        # only add the object layer
                        self.mentalMap[r][c] = []
                        for entity in entityLayer[r][c]:
                            if (entity.layer == Layer.OBJECT_LAYER or
                                entity.layer == Layer.WALL_LAYER):
                                self.mentalMap[r][c].append(entity)

        # add light layer to FOV
        for r,row in enumerate(lightLayer):
            for c,col in enumerate(row):
                if col:
                    self.mentalMap[r][c] = entityLayer[r][c]

    def clearMentalMap(self, entityLayer):
        '''Clears the mental map'''
        self.mentalMap = [[[] for _ in range(len(entityLayer[row]))]
                                for row in range(len(entityLayer))]

    def getSimpleFOV(self):
        '''Use a one layer circle to get which points are visible'''
        pts = []
        for pt in self.fovPoints:
            row = pt[0]+self.pos[0]
            col = pt[1]+self.pos[1]
            pts.append((row,col))
        return pts
    
    def fire(self, entityLayer, event):
        '''
        Throw an object
        '''
        if len(event) == 1:
            # zap to target
            pts = self.Brain.getFOVFromEntityLayer(entityLayer, self.pos)
            targetPos = []
            for pt in pts:
                for entity in entityLayer[pt[0]][pt[1]]:
                    if (self.attackable(entity) and 
                        (not targetPos or
                        math.dist(self.pos,entity.pos) <
                        math.dist(self.pos,targetPos))
                        ):
                        targetPos = list(entity.pos)
            if targetPos:
                return self.throw(Dart(), entityLayer, target=targetPos)
            else:
                Messager().addMessage('No targets!')
        else:
            # throw in a direction
            if event[1].isdigit():
                direction = ONE_LAYER_CIRCLE[int(event[1])-1]
                return self.throw(Dart(), entityLayer, direction=direction)
