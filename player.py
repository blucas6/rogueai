from entity import Entity, Attack, Health
from colors import Colors

class Player(Entity):
    def __init__(self):
        super().__init__('Player', '@', Colors().white, 1)
        self.Alive = Health(10)
        self.Attack = Attack('Punch', 1)

    def update(self, entityLayer):
        pass