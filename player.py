from entity import Entity, Attack, Health, ONE_LAYER_CIRCLE
from colors import Colors
from algo import RecursiveShadow

class Player(Entity):
    def __init__(self, rows, cols):
        super().__init__('Player', '@', Colors().white, 1)
        self.Alive = Health(10)
        self.Attack = Attack('Punch', 1)
        self.mentalMapRows = rows
        self.mentalMapCols = cols
        self.mentalMap = [[[] for _ in range(cols)] for _ in range(rows)]
        self.fovPoints = ONE_LAYER_CIRCLE
        self.fovMemory = True
        self.sightRange = 4
        self.unknownGlyph = ' '
        self.unknownColor = Colors().white

    def update(self, entityLayer):
        # pts = self.getSimpleFOV()
        pts = self.getFOV(entityLayer)
        if not self.fovMemory:
            self.mentalMap = [[[] for _ in range(self.mentalMapCols)]
                                    for _ in range(self.mentalMapRows)]
        for pt in pts:
            self.mentalMap[pt[0]][pt[1]] = entityLayer[pt[0]][pt[1]]

    def clearMentalMap(self, entityLayer):
        self.mentalMap = [[[] for _ in range(self.mentalMapCols)]
                                for _ in range(self.mentalMapRows)]
        self.update(entityLayer)

    def getFOV(self, entityLayer):
        grid = [[max([x.layer for x in entityLayer[r][c]])
                 for c in range(self.mentalMapCols)]
                    for r in range(self.mentalMapRows)]
        return RecursiveShadow(grid, self.pos, self.sightRange, 1)

    def getSimpleFOV(self):
        pts = []
        for pt in self.fovPoints:
            row = pt[0]+self.pos[0]
            col = pt[1]+self.pos[1]
            pts.append((row,col))
        return pts