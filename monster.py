from entity import Entity, Health
from colors import Colors
from animation import Animator, Animation

class Jelly(Entity):
    def __init__(self):
        super().__init__('Jelly', 'j', Colors().blue, 1)
        self.Health = Health(3)

    def update(self, entityLayer):
        if not self.Health.alive:
            self.remove()

    def remove(self):
        frames = {}
        frames['1'] = [
            ['','' ,''],
            ['','*',''],
            ['','' ,'']
        ]
        frames['2'] = [
            ['' ,'_', ''],
            ['/','' ,'/'],
            ['' ,'_', '']
        ]
        apos = [0,0]
        apos[0] = self.pos[0]-1
        apos[1] = self.pos[1]-1
        animation = Animation(apos, frames, Colors().white)
        animator = Animator()
        animator.queueUp(animation)
        super().remove()