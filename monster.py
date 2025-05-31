from entity import Entity 
from colors import Colors
from animation import Animator, Animation
from component import *

class Jelly(Entity):
    '''
    Jelly entity
    '''
    def __init__(self):
        super().__init__('Jelly', 'j', Colors().blue, 1)
        self.Health = Health(3)
        self.Attack = Attack('Splash', 5, Alignment.CHAOTIC)

    def remove(self, entityLayer):
        '''
        Generate the explosion on death
        '''
        self.Messager.addMessage('It explodes!')
        frames = {}
        frames['0'] = [
            ['','' ,''],
            ['','*',''],
            ['','' ,'']
        ]
        frames['1'] = [
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
            if self.validSpace(entityLayer, row, col):
                for entity in entityLayer[row][col]:
                    if hasattr(entity, 'Health'):
                        if entity.Health.changeHealth(-1*self.Attack.damage):
                            entity.remove(entityLayer)
        super().remove(entityLayer)

class Newt(Entity):
    '''
    Newt Entity
    '''
    def __init__(self):
        super().__init__('Newt', 'n', Colors().yellow, 1)
        self.Health = Health(3)
        self.Attack = Attack('Bite', 1, Alignment.CHAOTIC)
        self.Brain = Brain(5, 1)

    def input(self, energy, entityLayer, playerPos):
        if energy > 0:
            return self.doAction(
                    self.Brain.input(self.pos,playerPos, entityLayer),
                    entityLayer
                )
        return []
