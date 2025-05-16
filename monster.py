from entity import Entity, Health, ONE_LAYER_CIRCLE, Attack
from colors import Colors
from animation import Animator, Animation
from menu import Messager

class Jelly(Entity):
    '''
    Jelly entity
    '''
    def __init__(self):
        super().__init__('Jelly', 'j', Colors().blue, 1)
        self.Health = Health(3)
        self.Attack = Attack('Splash', 5)
        '''health bar'''

    def update(self, entityLayer):
        pass

    def remove(self, entityLayer):
        '''
        Generate the explosion on death
        '''
        frames = {}
        frames['1'] = [
            ['','' ,''],
            ['','*',''],
            ['','' ,'']
        ]
        frames['2'] = [
            ['/' ,'-', '\\'],
            ['|','' ,'|'],
            ['\\' ,'-', '/']
        ]
        apos = [0,0]
        apos[0] = self.pos[0]-1
        apos[1] = self.pos[1]-1
        animation = Animation(apos, frames, Colors().white)
        animator = Animator()
        animator.queueUp(animation)
        # spread damage
        points = ONE_LAYER_CIRCLE
        for point in points:
            row = self.pos[0] + point[0]
            col = self.pos[1] + point[1]
            if (row,col) == self.pos:
                continue
            self.Logger.log(f'{self.pos} {row} {col}')
            if self.validSpace(entityLayer, row, col):
                for entity in entityLayer[row][col]:
                    if hasattr(entity, 'Health'):
                        if entity.Health.changeHealth(-1*self.Attack.damage):
                            entity.remove(entityLayer)
        super().remove(entityLayer)