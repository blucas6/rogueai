from entity import Entity
from colors import Colors
from component import *

class Light(Entity):
    def __init__(self):
        self.Activate = Activate(False)
        '''Controls whether the light is on'''
        super().__init__('Light', '+', Colors().yellow, 0)

    def update(self, entityLayer, playerPos, lightLayer, *args):
        if self.Activate.active:
            for pt in ONE_LAYER_CIRCLE:
                lightLayer[pt[0]][pt[1]] = 1