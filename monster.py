from entity import Entity, Alive
from colors import Colors

class Jelly(Entity):
    def __init__(self):
        super().__init__('Jelly', 'j', Colors().blue, 1)
        self.Alive = Alive(3)

    def update(self, entityLayer):
        if not self.Alive.alive:
            self.isActive = False