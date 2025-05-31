from entity import Entity, Wall, Floor, StairUp, StairDown
from monster import *
from player import Player
from logger import Logger
import random
from algo import dijkstra

class Level:
    '''
    Level objects contain the map and handle the entity layer
    '''
    def __init__(self, height, width, z, rng):
        self.height = height
        '''Total height (rows) of the level'''
        self.width = width
        '''Total width (cols) of the level'''
        self.z = z
        '''Depth level'''
        self.EntityLayer = [[[] for _ in range(self.width)]
                                for _ in range(self.height)]
        '''Holds all entities on the level'''
        self.LightLayer = [[[] for _ in range(self.width)]
                                for _ in range(self.height)]
        '''Tracks all lit spaces on level'''
        self.RNG = rng
        '''Random generator with optional seed'''
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
        r = pos[0]
        c = pos[1]
        if self.withinMap(pos):
            if not overwrite and self.EntityLayer[r][c]:
                maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                if entity.layer <= maxLayer:
                    return                 
            if overwrite:
                self.EntityLayer[r][c] = [entity]
                entity.setPosition(pos, self.z, 0)
            else:
                self.EntityLayer[r][c].append(entity)
                entity.setPosition(pos, self.z, len(self.EntityLayer[r][c])-1)
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

    def generateMonsters(self):
        for r in range(self.height):
            for c in range(self.width):
                maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                if (maxLayer == 0 and self.RNG.randint(1,100) < 3):
                    if self.RNG.randint(1,2) == 1:
                        m = Jelly()
                    else:
                        m = Newt()
                    self.placeEntity(m, [r,c])

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
        if len(self.Levels) > 0 and z < len(self.Levels):
            self.Levels[z].placeEntity(self.Player, pos)
        else:
            self.Logger.log(f'Invalid placement of player!')

    def updateCurrentLevel(self, turn, energy):
        '''
        Go through current level layer and update entities, if an entity has 
        updated its own position, move it to the right spot
        Update the player first before everything
        Run through entity layer again to correct any positional changes
        Clear light layer and update lighting
        '''
        level = self.Levels[self.CurrentZ]

        # clear light layer
        self.LightLayer = [[[] for _ in range(self.width)]
                                for _ in range(self.height)]
        # get list of all entities to update
        entityStack = [entity for row in level.EntityLayer 
                            for entityList in row for entity in entityList]
        # make sure player updates first
        entityStack.append(self.Player)
        while entityStack:
            addEntities = []
            entity = entityStack.pop()
            # call entity update
            if not self.removeIfDead(entity, level):
                if entity.turn < turn:
                    entity.turn = turn
                    entities = entity.input(energy,
                                            level.EntityLayer,
                                            self.Player.pos
                                            )
                    if entities:
                        addEntities.append(entities)
                entities = entity.update(level.EntityLayer, self.Player.pos)
                if entities:
                    addEntities.append(entities)
                if addEntities:
                    for e in addEntities:
                        entityStack.append(e)
                # move entity to correct position
                self.fixEntityPosition(entity, level)

    def setupPlayerFOV(self):
        self.Logger.log(self.CurrentZ)
        self.Logger.log(self.getCurrentLevel())
        self.Player.setupFOV(self.getCurrentLevel().EntityLayer)

    def removeIfDead(self, entity: Entity, level: Level):
        '''
        Checks if an entity is still valid on the level, otherwise it will
        remove it
        '''
        # remove entity from the level
        if not entity.isActive:
            r = entity.EntityLayerPos[0]
            c = entity.EntityLayerPos[1]
            idx = entity.EntityLayerPos[2]
            try:
                del level.EntityLayer[r][c][idx]
                self.Logger.log(f'REMOVING: {entity.name} {r},{c},{idx}')
            except Exception as e:
                self.Logger.log(f'Failed to remove {entity.name}:{r},{c},{idx}')
            return True
        return False
    
    def fixEntityPosition(self, entity: Entity, level: Level):
        '''
        Moves an entity to the correct spot in the Entity Layer according
        to its own position, fixes the entity's entityLayerPos coords
        '''
        # move entity around current level
        r = entity.EntityLayerPos[0]
        c = entity.EntityLayerPos[1]
        idx = entity.EntityLayerPos[2]
        if (entity.pos[0] != r or entity.pos[1] != c):
            # remove entity at old spot
            del level.EntityLayer[r][c][idx]
            # place new entity and update r, c, idx
            level.placeEntity(entity, entity.pos)
        # move entity to another level
        if (entity.z != self.CurrentZ and 
                entity.z < self.TotalLevels):
            try:
                # make sure the entity is not already moved to a new level
                if level.EntityLayer[r][c][idx].id == entity.id:
                    # remove entity at old spot
                    del level.EntityLayer[r][c][idx]
                    # place entity and update r, c, idx
                    self.Levels[entity.z].placeEntity(entity, entity.pos)
            except:
                self.Logger.log(f'Skipping moving {entity.name} to new level')

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
