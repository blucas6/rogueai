from entity import *
from colors import Colors
from component import *

class Wall(Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(name='Wall',
                         glyph='░',
                         color=Colors().white,
                         layer=Layer.WALL_LAYER,
                         size=Size.VERY_LARGE)

class Floor(Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__(name='Floor',
                         glyph='.',
                         color=Colors().white,
                         layer=Layer.FLOOR_LAYER,
                         size=Size.LARGE)

class StairUp(Entity):
    '''Up stair entity'''
    def __init__(self):
        super().__init__(name='Upstair',
                         glyph='<',
                         color=Colors().white,
                         layer=Layer.FLOOR_LAYER,
                         size=Size.VERY_LARGE)

class StairDown(Entity):
    '''Down stair entity'''
    def __init__(self):
        super().__init__(name='Downstair',
                         glyph='>',
                         color=Colors().white,
                         layer=Layer.FLOOR_LAYER,
                         size=Size.VERY_LARGE)

class Light(Entity):
    '''Light entity'''
    def __init__(self):
        super().__init__(name='Light',
                         glyph='+',
                         color=Colors().yellow,
                         layer=Layer.OBJECT_LAYER,
                         size=Size.SMALL)
        self.Activate = Activate(True)
        '''Controls whether the light is on'''

    def update(self, entityLayer, playerPos, lightLayer, *args):
        '''
        Turn the light on if it is active
        '''
        if self.Activate.active:
            points = getOneLayerPts(self.pos)
            for pt in points:
                lightLayer[pt[0]][pt[1]] = 1
    
class Dart(Entity):

    def __init__(self):
        super().__init__(name='Dart',
                         glyph=')',
                         color=Colors().red,
                         layer=Layer.OBJECT_LAYER,
                         size=Size.VERY_SMALL)