from entity import *
from colors import Colors
from component import *

class Bite(Entity):
    def __init__(self):
        super().__init__(name='Bite',
                         glyph='?',
                         color=Colors().magenta,
                         layer=Layer.OBJECT_LAYER,
                         size=Size.VERY_SMALL)
        self.Attack = Attack(name='Bite',
                             damage=1)

class Sword(Entity):
    def __init__(self):
        super().__init__(name='Sword',
                         glyph='/',
                         color=Colors().blue,
                         layer=Layer.OBJECT_LAYER,
                         size=Size.SMALL)
        self.Attack = Attack(name='Slash',
                             damage=2)