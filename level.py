from entity import Entity, Wall, Floor, StairUp, StairDown
from player import Player
from logger import Logger
import random

class LevelManager:
    '''
    LevelManager class contains all level objects and dictates what the game
    class will display
    '''
    def __init__(self, height: int=0, width: int=0, origin: tuple=(0,0),
        levels=0):
        self.height = height
        '''total height (rows) in the map'''
        self.width = width
        '''total width (cols) in the map'''
        self.origin = origin
        '''top left corner of map in relation to the screen buffer'''
        self.Levels = []
        '''holds all level objects'''
        self.TotalLevels = levels
        '''how many levels to hold'''
        self.CurrentZ = 0
        '''current level indicator'''
        self.Player = None
        '''player object'''
        self.Logger = Logger()
        for l in range(self.TotalLevels):
            self.Levels.append(Level(self.height, self.width, l))
        
    def defaultSetUp(self):
        '''
        Load a default map on all levels
        '''
        downstairPos = []
        for level in self.Levels:
            if level == self.Levels[-1]:
                downstairPos = level.default(downstairPos, upstair=False)
            else:
                downstairPos = level.default(downstairPos)

    def addPlayer(self, pos: list, z: int):
        '''
        Create the player object and add him to the map
        '''
        self.Player = Player()
        self.Player.setPosition(pos, z)
        if len(self.Levels) > 0:
            self.Levels[self.Player.z].addEntity(self.Player)

    def updateCurrentLevel(self):
        '''
        Go through current level layer and update entities, if an entity has 
        updated its own position, move it to the right spot
        '''
        level = self.Levels[self.CurrentZ]
        for r,row in enumerate(level.EntityLayer):
            for c,col in enumerate(row):
                entityList = level.EntityLayer[r][c]
                if not entityList:
                    continue
                for idx,entity in enumerate(entityList):
                    entity.update(level.EntityLayer)
                    # move entity to another level
                    if (entity.z != self.CurrentZ and 
                                entity.z < self.TotalLevels):
                        if self.Levels[entity.z].addEntity(entity):
                            del level.EntityLayer[r][c][idx]
                    # move entity around current level
                    elif (entity.pos[0] != r or entity.pos[1] != c):
                        if level.addEntity(entity):
                            del level.EntityLayer[r][c][idx]
    
    def swapLevels(self):
        '''
        Check if the Player object has moved to a different level
        '''
        if self.Player.z != self.CurrentZ:
            self.CurrentZ = self.Player.z
            return True
        return False

    def getCurrentLevel(self):
        '''
        Returns the current level object
        '''
        return self.Levels[self.CurrentZ]

class Level:
    '''
    Level objects contain the map and handle the entity layer
    '''
    def __init__(self, height, width, z):
        self.height = height
        '''total height (rows) of the level'''
        self.width = width
        '''total width (cols) of the level'''
        self.z = z
        '''depth level'''
        self.EntityLayer = [[[] for _ in range(self.width)]
                                for _ in range(self.height)]
        '''holds all entities on the level'''
        self.Logger = Logger()

    def default(self, downstairPos=[], upstair=True):
        '''loads a default map'''
        for r in range(self.height):
            for c in range(self.width):
                if r == 0 or c == 0 or r == self.height-1 or c == self.width-1:
                    entity = Wall()
                else:
                    entity = Floor()
                self.EntityLayer[r][c] = [entity]
                entity.setPosition((r,c), self.z)
        # add stairs
        if downstairPos:
            entity = StairDown()
            entity.setPosition(downstairPos, self.z)
            self.EntityLayer[downstairPos[0]][downstairPos[1]] = [entity]
        if upstair:
            upstairPos = [random.randint(1,self.height-2),
                                            random.randint(1,self.width-2)]
            entity = StairUp()
            entity.setPosition(upstairPos, self.z)
            self.EntityLayer[upstairPos[0]][upstairPos[1]] = [entity]
            return upstairPos
        return [-1,-1]

    def withinMap(self, pos):
        '''returns if a position is valid within the map'''
        if (pos[0] < len(self.EntityLayer) and 
            pos[1] < len(self.EntityLayer[0]) and pos[0] >= 0 and pos[1] >= 0):
            return True
        return False

    def addEntity(self, entity: Entity):
        '''
        Adds an entity to the layer according to its position
        '''
        if self.withinMap(entity.pos):
            self.EntityLayer[entity.pos[0]][entity.pos[1]].append(entity)
            return True
        else:
            self.Logger.log(f'Invalid addition to entity layer!')
            self.Logger.log(f'   {entity.name} @ {entity.pos} z:{entity.z}')
            return False