from entity import *
from component import *
from colors import Colors

class Player(Entity):
    def __init__(self, rows, cols):
        super().__init__(name='Player',
                         glyph='@',
                         color=Colors().white,
                         layer=Layer.MONST_LAYER)
        self.Health = Health(health=6)
        '''Health component'''
        self.Attack = Attack(name='Punch',
                             damage=1,
                             alignment=Alignment.LAWFUL)
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
        self.blockLayer = Layer.WALL_LAYER
        '''For FOV, highest level (exclusive) to see through'''
        self.Brain = Brain(self.sightRange, self.blockLayer)
        '''Player brain for game interactions'''

    def input(self, energy, entityLayer, playerPos, playerZ, event):
        return self.doAction(event, entityLayer)

    def setupFOV(self, entityLayer, lightLayer):
        '''Get the FOV for the player'''
        # pts = self.getSimpleFOV()
        pts = self.Brain.getFOVFromEntityLayer(entityLayer, self.pos)
        if not self.fovMemory:
            self.mentalMap = [[[] for _ in range(len(entityLayer[row]))]
                                    for row in range(len(entityLayer))]
        for pt in pts:
            self.mentalMap[pt[0]][pt[1]] = entityLayer[pt[0]][pt[1]]
        
        for r,row in enumerate(lightLayer):
            for c,col in enumerate(row):
                if col:
                    self.mentalMap[r][c] = entityLayer[r][c]

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