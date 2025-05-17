from entity import Entity, Attack, Health, ONE_LAYER_CIRCLE
from colors import Colors

class Player(Entity):
    def __init__(self, rows, cols):
        super().__init__('Player', '@', Colors().white, 1)
        self.Alive = Health(10)
        self.Attack = Attack('Punch', 1)
        self.mentalMapRows = rows
        self.mentalMapCols = cols
        self.mentalMap = [[[] for _ in range(rows)] for _ in range(cols)]
        self.sightRange = ONE_LAYER_CIRCLE
        self.unknownGlyph = ' '
        self.unknownColor = Colors().white

    def update(self, entityLayer):
        for pt in self.sightRange:
            row = pt[0]+self.pos[0]
            col = pt[1]+self.pos[1]
            self.mentalMap[row][col] = entityLayer[row][col]

    def clearMentalMap(self, entityLayer):
        self.mentalMap = [[[] for _ in range(self.mentalMapRows)]
                                for _ in range(self.mentalMapCols)]
        self.update(entityLayer)