from entity import *
from colors import Colors
from component import *

class Wall(Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(name='Wall',
                         glyph='░',
                         color=Colors().white,
                         layer=Layer.WALL_LAYER)

class Floor(Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__(name='Floor',
                         glyph='.',
                         color=Colors().white,
                         layer=Layer.FLOOR_LAYER)

class StairUp(Entity):
    '''Up stair entity'''
    def __init__(self):
        super().__init__(name='Upstair',
                         glyph='<',
                         color=Colors().white,
                         layer=Layer.FLOOR_LAYER)

class StairDown(Entity):
    '''Down stair entity'''
    def __init__(self):
        super().__init__(name='Downstair',
                         glyph='>',
                         color=Colors().white,
                         layer=Layer.FLOOR_LAYER)

class Light(Entity):
    def __init__(self):
        super().__init__(name='Light',
                         glyph='+',
                         color=Colors().yellow,
                         layer=Layer.OBJECT_LAYER)
        self.Activate = Activate(False)
        '''Controls whether the light is on'''

    def update(self, entityLayer, playerPos, lightLayer, *args):
        if self.Activate.active:
            points = getOneLayerPts(self.pos)
            for pt in points:
                lightLayer[pt[0]][pt[1]] = 1
        return []