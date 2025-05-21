from entity import Entity, ONE_LAYER_CIRCLE
from component import *
from colors import Colors
from algo import RecursiveShadow

class Player(Entity):
    def __init__(self, rows, cols):
        super().__init__('Player', '@', Colors().white, 1)
        self.Health = Health(20)
        '''Health component'''
        self.Attack = Attack('Punch', 1, Alignemnt.LAWFUL)
        '''Attack component'''
        self.mentalMapSize = [rows, cols]
        '''Size of the mental map for FOV'''
        self.mentalMap = [[[] for _ in range(cols)] for _ in range(rows)]
        '''Entity map for output to the screen'''
        self.fovPoints = ONE_LAYER_CIRCLE
        '''Used for simple FOV'''
        self.fovMemory = True
        '''Decides if FOV gets clear or stays in memory'''
        self.sightRange = 4
        '''How far the FOV will check'''
        self.unknownGlyph = ' '
        '''Glyph to show unexplored territory'''
        self.unknownColor = Colors().white
        '''Color of glyph for unexplored territory'''

    def update(self, entityLayer, *args):
        # pts = self.getSimpleFOV()
        pts = self.getFOV(entityLayer)
        if not self.fovMemory:
            self.mentalMap = [[[] for _ in range(self.mentalMapSize[1])]
                                    for _ in range(self.mentalMapSize[0])]
        for pt in pts:
            self.mentalMap[pt[0]][pt[1]] = entityLayer[pt[0]][pt[1]]

    def clearMentalMap(self, entityLayer):
        '''Clears the mental map'''
        self.mentalMap = [[[] for _ in range(self.mentalMapSize[1])]
                                for _ in range(self.mentalMapSize[0])]
        self.update(entityLayer)

    def getFOV(self, entityLayer):
        '''Use FOV algorithm to get which points are visible'''
        grid = [[max([x.layer for x in entityLayer[r][c]])
                 for c in range(self.mentalMapSize[1])]
                    for r in range(self.mentalMapSize[0])]
        return RecursiveShadow(grid, self.pos, self.sightRange, 1)

    def getSimpleFOV(self):
        '''Use a one layer circle to get which points are visible'''
        pts = []
        for pt in self.fovPoints:
            row = pt[0]+self.pos[0]
            col = pt[1]+self.pos[1]
            pts.append((row,col))
        return pts