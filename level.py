from entity import Entity, Wall, Floor, StairUp, StairDown
from monster import *
from player import Player
from logger import Logger
import random
from algo import dijkstra

class LevelManager:
    '''
    LevelManager class contains all level objects and dictates what the game
    class will display
    '''
    def __init__(self, rng, height: int=0, width: int=0, origin: tuple=(0,0),
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
            self.Levels.append(Level(self.height, self.width, l, rng))
        
    def defaultLevelSetup(self, playerPos):
        '''
        Load a default map on all levels
        '''
        downstairPos = []
        for level in self.Levels:
            if level == self.Levels[-1]:
                downstairPos = level.default(
                    downstairPos=downstairPos, upstair=False)
            elif level == self.Levels[0]:
                downstairPos = level.default(
                    playerPos=playerPos, downstairPos=downstairPos)
            else:
                downstairPos = level.default(downstairPos=downstairPos)
            level.generateMonsters()

    def defaultLevelSetupWalls(self, playerPos):
        '''
        Load a default map with some walls
        '''
        downstairPos = []
        for level in self.Levels:
            if level == self.Levels[-1]:
                downstairPos = level.defaultWalls(
                    downstairPos=downstairPos, upstair=False)
            elif level == self.Levels[0]:
                downstairPos = level.defaultWalls(
                    playerPos=playerPos, downstairPos=downstairPos)
            else:
                downstairPos = level.defaultWalls(downstairPos=downstairPos)
            level.generateMonsters()

    def addPlayer(self, pos: list, z: int):
        '''
        Create the player object and add him to the map
        '''
        self.Player = Player(self.height, self.width)
        self.Player.setPosition(pos, z)
        if len(self.Levels) > 0:
            self.Levels[self.Player.z].addEntity(self.Player)

    def updateCurrentLevel(self):
        '''
        Go through current level layer and update entities, if an entity has 
        updated its own position, move it to the right spot
        Update the player first before everything
        Run throught entity layer again to correct any positional changes
        '''
        level = self.Levels[self.CurrentZ]
        # update player positioning first
        self.fixPlayerPosition(level)
        # update all entities normally
        for r,row in enumerate(level.EntityLayer):
            for c,entityList in enumerate(row):
                if not entityList:
                    continue
                for idx,entity in enumerate(entityList):
                    # call entity update
                    if not self.checkForDeath(entity, level, r, c, idx):
                        entity.update(level.EntityLayer, self.Player.pos)
        # move all entities to the correct spot
        for r,row in enumerate(level.EntityLayer):
            for c,entityList in enumerate(row):
                if not entityList:
                    continue
                for idx,entity in enumerate(entityList):
                    if not self.checkForDeath(entity, level, r, c, idx):
                        # move entity to correct position
                        self.fixEntityPosition(entity, level, r, c, idx)

    def checkForDeath(self, entity, level, r, c, idx):
        '''
        Checks if an entity is still valid on the level, otherwise it will
        remove it
        '''
        # remove entity from the level
        if not entity.isActive:
            del level.EntityLayer[r][c][idx]
            return True
        return False
    
    def fixEntityPosition(self, entity, level, r, c, idx):
        '''
        Moves an entity to the correct spot in the Entity Layer according
        to its own position
        '''
        # move entity to another level
        if (entity.z != self.CurrentZ and 
                    entity.z < self.TotalLevels):
            if self.Levels[entity.z].addEntity(entity):
                del level.EntityLayer[r][c][idx]
        # move entity around current level
        elif (entity.pos[0] != r or entity.pos[1] != c):
            if level.addEntity(entity):
                del level.EntityLayer[r][c][idx]
    
    def fixPlayerPosition(self, level):
        '''
        Finds the Player in the Entity Layer and moves it to its correct spot
        according to its own position
        '''
        for r,row in enumerate(level.EntityLayer):
            for c,entityList in enumerate(row):
                if not entityList:
                    continue
                for idx,entity in enumerate(entityList):
                    if entity.name == 'Player':
                        self.fixEntityPosition(entity, level, r, c, idx)
                        return

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
    def __init__(self, height, width, z, rng):
        self.height = height
        '''total height (rows) of the level'''
        self.width = width
        '''total width (cols) of the level'''
        self.z = z
        '''depth level'''
        self.EntityLayer = [[[] for _ in range(self.width)]
                                for _ in range(self.height)]
        '''holds all entities on the level'''
        self.RNG = rng
        '''random generator with optional seed'''
        self.Logger = Logger()

    def default(self, playerPos=[], downstairPos=[], upstair=True):
        '''loads a default map'''
        # generate walls and floor
        self.generateSurroundingWallsFloor()
        # add stairs
        return self.generateStairs(
            playerPos=playerPos, downstairPos=downstairPos, upstair=upstair)
    
    def defaultWalls(self, playerPos=[], downstairPos=[], upstair=True):
        '''loads a map with some walls'''
        # generate walls and floor
        self.generateSurroundingWallsFloor()
        # add wall shapes
        self.wallShapeGenerator(playerPos=playerPos, minWallsPlaced=45)
        # add stairs
        return self.generateStairs(
            playerPos=playerPos, downstairPos=downstairPos, upstair=upstair)

    def wallShapeGenerator(self, playerPos=[], minWallsPlaced=10):
        '''
        Generates walls on the level using predetermined shapes
        minWallsPlaced counts how many wall spaces need to be covered in the 
        level
        '''
        self.Logger.log(playerPos)
        wallShapes = []
        wallL = [
            ['0','',''],
            ['0','',''],
            ['0','0','0']
        ]
        wallPlus = [
            ['','0',''],
            ['0','0','0'],
            ['','0','']
        ]
        wallLine = [
            ['','0',''],
            ['','0',''],
            ['','0','']
        ]
        wallCorner = [
            ['','',''],
            ['0','',''],
            ['0','0','']
        ]
        wallShapes.append(wallL)
        wallShapes.append(wallPlus)
        wallShapes.append(wallLine)
        wallShapes.append(wallCorner)
        wallsPlaced = 0
        maxIterations = 10
        while wallsPlaced < minWallsPlaced and maxIterations > 0:
            maxIterations -= 1
            for r in range(self.height):
                for c in range(self.width): 
                    maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                    if maxLayer < 1 and self.RNG.randint(1,100) < 10:
                        shape = wallShapes[self.RNG.randint(0,len(wallShapes)-1)]
                        times = self.RNG.randint(0,3)
                        for t in range(times):
                            shape = [list(row) for row in zip(*shape[::-1])]
                        for sr,srows in enumerate(shape):
                            for sc,scols in enumerate(srows):
                                pt = [r+sr,c+sc]
                                if not scols:
                                    continue
                                if playerPos and pt == playerPos:
                                    continue
                                self.placeEntity(Wall(), pt)
                                wallsPlaced += 1

    def placeEntity(self, entity: Entity, pos, overwrite=False):
        '''
        Places an entity somewhere valid on the map
        Overwrite set to true will delete any other entities at that position
        Overwrite set to false will simply append
        '''
        if self.withinMap(pos):
            if not overwrite and self.EntityLayer[pos[0]][pos[1]]:
                maxLayer = max([x.layer for x in self.EntityLayer[pos[0]][pos[1]]])
                if entity.layer <= maxLayer:
                    return                 
            entity.setPosition(pos, self.z)
            if overwrite:
                self.EntityLayer[pos[0]][pos[1]] = [entity]
            else:
                self.EntityLayer[pos[0]][pos[1]].append(entity)
        else:
            self.Logger.log(f'Failed to place entity -> {entity.name} {pos}')

    def generateStairs(self, playerPos=[], downstairPos=[], upstair=True):
        '''
        Adds downstairs if there was a previous upstairs on the level below
        Adds upstairs somewhere random
        Makes sure there is a path between stair wells
        '''
        # add stairs
        upstairPos = [-1,-1]
        if downstairPos:
            self.placeEntity(StairDown(), downstairPos, overwrite=True)
        if upstair:
            upstairPos = [self.RNG.randint(1,self.height-2),
                                            self.RNG.randint(1,self.width-2)]
            self.placeEntity(StairUp(), upstairPos, overwrite=True)
        else:
            # no need to path check if last level
            return upstairPos
        # create a path between stair wells
        start = downstairPos
        if not downstairPos:
            start = playerPos
        end = upstairPos
        grid = [[max([e.layer for e in el]) for el in row]
                    for row in self.EntityLayer]
        pts = dijkstra(grid, tuple(start), tuple(end))
        for pt in pts:
            if pt == pts[0] or pt == pts[-1]:
                continue
            self.placeEntity(Floor(),pt,overwrite=True)
        return upstairPos

    def generateSurroundingWallsFloor(self):
        '''
        Adds surrounding walls and floor to a blank entity array
        '''
        for r in range(self.height):
            for c in range(self.width):
                # check if within the array or on the border
                if r == 0 or c == 0 or r == self.height-1 or c == self.width-1:
                    self.placeEntity(Wall(),[r,c],overwrite=True)
                else:
                    self.placeEntity(Floor(),[r,c],overwrite=True)

    def withinMap(self, pos):
        '''
        Returns if a position is valid within the map
        '''
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

    def generateMonsters(self):
        for r in range(self.height):
            for c in range(self.width):
                maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                if (maxLayer == 0 and self.RNG.randint(1,100) < 3):
                    if self.RNG.randint(1,2) == 1:
                        m = Jelly()
                    else:
                        m = Newt()
                    m.setPosition([r,c], self.z)
                    self.EntityLayer[r][c].append(m)