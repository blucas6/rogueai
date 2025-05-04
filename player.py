from entity import Entity
from colors import Colors

class Player(Entity):
    def __init__(self):
        super().__init__('Player', '@', Colors().white, 1)

    def update(self, entityLayer):
        self.Logger.log(f'player {self.pos} z:{self.z}')