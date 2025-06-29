from entity import *
from monster import *
from tower import *
from player import Player
from logger import Logger, Timing
from animation import *
from algo import dijkstra
import copy

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
        self.LightLayer = [[0 for _ in range(self.width)]
                                for _ in range(self.height)]
        '''Tracks all lit spaces on level'''
        self.RNG = rng
        '''Random generator with optional seed'''
        self.Logger = Logger()

    def default(self, playerPos=[], downstairPos=[], upstair=True):
        '''Loads a default map'''
        # generate walls and floor
        self.generateSurroundingWallsFloor()
        # add stairs
        return self.generateStairs(
            playerPos=playerPos, downstairPos=downstairPos, upstair=upstair)
    
    def defaultWalls(self, playerPos=[], downstairPos=[], upstair=True):
        '''Loads a map with some walls'''
        # generate walls and floor
        self.generateSurroundingWallsFloor()
        # add wall shapes
        self.wallShapeGenerator(playerPos=playerPos, minWallsPlaced=45)
        # add stairs
        return self.generateStairs(
            playerPos=playerPos, downstairPos=downstairPos, upstair=upstair)

    def addLighting(self):
        '''
        Adds lights to the level
        '''
        for r in range(self.height):
            for c in range(self.width):
                maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                if (maxLayer == Layer.FLOOR_LAYER
                    and self.RNG.randint(1,100) < 3):
                    self.placeEntity(Light(), [r,c])

    def wallShapeGenerator(self, playerPos=[], minWallsPlaced=10):
        '''
        Generates walls on the level using predetermined shapes
        minWallsPlaced counts how many wall spaces need to be covered in the 
        level
        '''
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
        maxIterations = 100
        # go through until minimum wall amount was reached or max tries
        while wallsPlaced < minWallsPlaced and maxIterations > 0:
            maxIterations -= 1
            for r in range(self.height):
                for c in range(self.width): 
                    if self.RNG.randint(1,100) < 10:
                        # grab a shape and rotate it
                        shape = wallShapes[self.RNG.randint(0,len(wallShapes)-1)]
                        times = self.RNG.randint(0,3)
                        for t in range(times):
                            shape = [list(row) for row in zip(*shape[::-1])]
                        for sr,srows in enumerate(shape):
                            for sc,scols in enumerate(srows):
                                pt = [r+sr,c+sc]
                                # not a point in the shape
                                if not scols:
                                    continue
                                # player is already there
                                if playerPos and pt == playerPos:
                                    continue
                                self.placeEntity(Wall(), pt)
                                wallsPlaced += 1

    def findFreeSpace(self, entity: Entity, pos: list):
        '''
        If an entity can't be placed on the spot it was specified for,
        find other available points around
        '''
        # check first point
        r,c = pos[0], pos[1]
        maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
        if entity.layer > maxLayer:
            return [r,c]
        # check for surrounding points that are open
        points = getOneLayerPts(pos)
        for pt in points:
            r,c = pt[0], pt[1]
            maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
            if entity.layer > maxLayer:
                return [r,c]
        return [-1,-1]

    def placeEntity(self, entity: Entity, pos, overwrite=False, specific=True):
        '''
        Places an entity somewhere valid on the map
        Overwrite set to true will delete any other entities at that position
        Overwrite set to false will simply append
        Specific is used when a spot may be filled by another entity (going to 
        a new level by stairs), False let's placement be around the position
        '''
        r = pos[0]
        c = pos[1]
        if self.withinMap(pos):
            if overwrite:
                # if overwriting, specific position will always work
                self.EntityLayer[r][c] = [entity]
                entity.setPosition(pos=pos, zlevel=self.z, idx=0)
            else:
                # if appending, position may be full
                if entity.layer > Layer.OBJECT_LAYER:
                    # entities that have a large layer (greater than 1)
                    # are not able to be placed on top of another large layer
                    if not specific:
                        r,c = self.findFreeSpace(entity, pos)
                    maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                    if entity.layer <= maxLayer:
                        self.Logger.log(f'Error: layer issue with placement -> {entity.name} {maxLayer} {self.EntityLayer[r][c]}')
                        return
                self.EntityLayer[r][c].append(entity)
                entity.setPosition(pos=pos,
                                zlevel=self.z,
                                idx=len(self.EntityLayer[r][c])-1)
                # self.Logger.log(f'Placing entity -> {entity.name} {pos}')
        else:
            self.Logger.log(f'Error: entity outside of map -> {entity.name} {pos}')

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
        pts = dijkstra(grid, tuple(start), tuple(end), diagonals=False)
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

    def generateMonsters(self, playerPos):
        for r in range(self.height):
            for c in range(self.width):
                if [r,c] == playerPos:
                    continue
                maxLayer = max([x.layer for x in self.EntityLayer[r][c]])
                if (maxLayer == Layer.FLOOR_LAYER
                    and self.RNG.randint(1,100) < 3):
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
    def __init__(self, game, rng, height: int=0, width: int=0, origin: tuple=(0,0),
        levels=0):
        self.Game = game
        '''Reference to game object'''
        self.height = height
        '''Total height (rows) in the map'''
        self.width = width
        '''Total width (cols) in the map'''
        self.origin = origin
        '''Top left corner of map in relation to the screen buffer'''
        self.Levels = []
        '''Holds all level objects'''
        self.TotalLevels = levels
        '''How many levels to hold'''
        self.CurrentZ = 0
        '''Current level indicator'''
        self.Player = None
        '''Player object'''
        self.Animator = Animator()
        '''Animation manager'''
        self.Timing = Timing()
        '''Timing recorder'''
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
            level.generateMonsters(playerPos)
            level.addLighting()

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
            level.generateMonsters(playerPos)
            level.addLighting()

    def addPlayer(self, pos: list, z: int):
        '''
        Create the player object and add him to the map
        '''
        self.Player = Player(self.height, self.width)
        if len(self.Levels) > 0 and z < len(self.Levels):
            self.Levels[z].placeEntity(self.Player, pos)
        else:
            self.Logger.log(f'Error: invalid placement of player!')

    def updateCurrentLevel(self, playerEvent, turn, energy):
        '''
        Go through current level layer and update entities
        
        If an entity has 
        updated its own position, move it to the right spot

        Update the player first before everything

        Pass the player's action to the player entity

        Entities that affect other entities add those entities to the stack to
        be updated next

        Clear the light array every loop

        Play the animations generated from an entity turn
        '''
        # timing
        self.Timing.start('Game Loop')

        level = self.Levels[self.CurrentZ]

        # clear light layer
        level.LightLayer = [[0 for _ in range(self.width)]
                                for _ in range(self.height)]
        # get list of all entities to update
        entityStack = [entity for row in level.EntityLayer 
                            for entityList in row for entity in entityList]
        # make sure player updates first
        entityStack.append(self.Player)
        while entityStack:
            addEntities = []
            entity = entityStack.pop()
            fromInput = []  # add to stack, came from input
            fromUpdate = [] # add to stack, came from update
            fromDeath = []  # add to stack, came from death
            isDead, fromDeath = self.removeIfDead(entity, level)
            if not isDead:
                # entity is alive
                if entity.turn < turn:
                    # entity has not yet taken a turn
                    entity.turn = turn
                    fromInput = entity.input(energy,
                                            level.EntityLayer,
                                            self.Player.pos,
                                            self.Player.z,
                                            playerEvent)
                # always call entity update
                fromUpdate = entity.update(level.EntityLayer,
                                         self.Player.pos,
                                         level.LightLayer)
                # move entity to correct position
                self.fixEntityPosition(entity, level)
            
            # add other entities affected to the stack
            if fromInput:
                addEntities.extend(fromInput)
            if fromUpdate:
                addEntities.extend(fromUpdate)
            if fromDeath:
                addEntities.extend(fromDeath)
            if addEntities:
                for e in addEntities:
                    if e:
                        self.Logger.log(f'Adding -> {e.name} {e.pos}')
                        entityStack.append(e)

            # play animations (could be queued from death)
            self.Timing.pause()
            self.animations()
            self.Timing.resume()
        self.Timing.end()

    def animations(self):
        '''
        Display animations
        '''
        if self.Animator.AnimationQueue:
            # save off screen buffer
            oldScreenBuffer = copy.deepcopy(self.Game.ScreenBuffer)
            oldColorBuffer = copy.deepcopy(self.Game.ColorBuffer)
            # animations have been queued
            frameCounter = 0
            maxFrames = max([len(list(x.frames.keys()))
                             for x in self.Animator.AnimationQueue])
            for frameCounter in range(maxFrames):
                # draw on the old buffer
                self.Game.ScreenBuffer = copy.deepcopy(oldScreenBuffer)
                self.Game.ColorBuffer = copy.deepcopy(oldColorBuffer)
                for animation in self.Animator.AnimationQueue:
                    if frameCounter >= len(list(animation.frames.keys())):
                        continue
                    ar, ac = animation.pos[0], animation.pos[1]
                    delay = animation.delay
                    # add frame array to the screen
                    for r,row in enumerate(animation.frames[str(frameCounter)]):
                        for c,col in enumerate(row):
                            if not col:
                                continue
                            rw, cl = self.Game.mapPosToScreenPos(ar+r,ac+c)
                            self.Game.ScreenBuffer[rw][cl] = col
                            self.Game.ColorBuffer[rw][cl] = animation.color
                # output to terminal
                self.Game.render()
                self.Game.Engine.pause(delay)
            # done with all animations
            self.Animator.clearQueue()

    def setupPlayerFOV(self):
        '''
        Get the FOV from the player object
        '''
        self.Player.setupFOV(self.getCurrentLevel().EntityLayer,
                             self.getCurrentLevel().LightLayer)

    def removeIfDead(self, entity: Entity, level: Level):
        '''
        Checks if an entity is still valid on the level, otherwise it will
        remove it
        '''
        if not entity.isActive:
            entities = []   # death may trigger other kills
            r = entity.EntityLayerPos[0]
            c = entity.EntityLayerPos[1]
            idx = entity.EntityLayerPos[2]
            if idx >= len(level.EntityLayer[r][c]):
                # not enough entity on the square for this entity to still be
                # here, must have already been removed
                return True, []
            try:
                if level.EntityLayer[r][c][idx].id == entity.id:
                    del level.EntityLayer[r][c][idx]
                    # call entity death ONLY if it is the same entity
                    entities = entity.death(level.EntityLayer)
                    self.Logger.log(f'REMOVING: {entity.name} {r},{c},{idx}')
            except Exception as e:
                self.Logger.log(f'Error: failed to remove {entity.name}:{r},{c},{idx}')
            return True, entities
        return False, []
    
    def fixEntityPosition(self, entity: Entity, level: Level):
        '''
        Moves an entity to the correct spot in the Entity Layer according
        to its own position, fixes the entity's entityLayerPos coords
        '''
        # check if entity has been placed on the level
        if entity.EntityLayerPos[2] == -1:
            # entity has just been created, not on level yet
            level.placeEntity(entity, entity.pos)
        else:
            # move entity around current level
            r = entity.EntityLayerPos[0]
            c = entity.EntityLayerPos[1]
            idx = entity.EntityLayerPos[2]
            if (entity.pos[0] != r or entity.pos[1] != c):
                # remove entity at old spot
                # self.Logger.log(f'Trying to remove -> {entity.name} {entity.isActive} {entity.EntityLayerPos} {entity.pos}')
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
                        self.Levels[entity.z].placeEntity(entity,
                                                        entity.pos,
                                                        specific=False)
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

    def getCurrentLevel(self) -> Level:
        '''
        Returns the current level object
        '''
        return self.Levels[self.CurrentZ]