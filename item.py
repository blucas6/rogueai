from entity import *
from color import Colors
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
        self.PickUp = PickUp()

class Sword(Entity):
    def __init__(self):
        super().__init__(name='Sword',
                         glyph='/',
                         color=Colors().blue,
                         layer=Layer.OBJECT_LAYER,
                         size=Size.SMALL)
        self.Attack = Attack(name='Slash',
                             damage=2)
        self.PickUp = PickUp()

class Dart(Entity):
    def __init__(self):
        super().__init__(name='Dart',
                         glyph=')',
                         color=Colors().red,
                         layer=Layer.OBJECT_LAYER,
                         size=Size.VERY_SMALL)
        self.PickUp = PickUp()