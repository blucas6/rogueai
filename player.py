from entity import Entity, ONE_LAYER_CIRCLE
from component import *
from colors import Colors
from algo import RecursiveShadow

class Player(Entity):
    def __init__(self, rows, cols):
        super().__init__('Player', '@', Colors().white, 1)
        self.Health = Health(20)
        '''Health component'''
        self.Attack = Attack('Punch', 1, Alignment.LAWFUL)
        '''Attack component'''
        self.mentalMap = [[[] for _ in range(cols)] for _ in range(rows)]
        '''Entity map for output to the screen'''
        self.fovPoints = ONE_LAYER_CIRCLE
        '''Used for simple FOV'''
        self.fovMemory = True
        '''Decides if FOV gets cleared or stays in memory'''
        self.sightRange = 4
        '''How far the FOV will check'''
        self.unknownGlyph = ' '
        '''Glyph to show unexplored territory'''
        self.unknownColor = Colors().white
        '''Color of glyph for unexplored territory'''
        self.blockLayer = 1
        '''For FOV, highest level (exclusive) to see through'''
        self.Brain = Brain(self.sightRange, self.blockLayer)
        '''Player brain for game interactions'''

    def update(self, entityLayer, *args):
        # pts = self.getSimpleFOV()
        pts = self.Brain.getFOVFromEntityLayer(entityLayer, self.pos)
        if not self.fovMemory:
            self.mentalMap = [[[] for _ in range(len(entityLayer[row]))]
                                    for row in range(len(entityLayer))]
        for pt in pts:
            self.mentalMap[pt[0]][pt[1]] = entityLayer[pt[0]][pt[1]]

    def clearMentalMap(self, entityLayer):
        '''Clears the mental map'''
        self.mentalMap = [[[] for _ in range(len(entityLayer[row]))]
                                for row in range(len(entityLayer))]
        self.update(entityLayer)

    def getSimpleFOV(self):
        '''Use a one layer circle to get which points are visible'''
        pts = []
        for pt in self.fovPoints:
            row = pt[0]+self.pos[0]
            col = pt[1]+self.pos[1]
            pts.append((row,col))
        return pts