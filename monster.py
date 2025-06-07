from entity import *
from colors import Colors
from animation import Animator, Animation
from component import *

class Jelly(Entity):
    '''
    Jelly entity
    '''
    def __init__(self):
        super().__init__(name='Jelly',
                         glyph='j',
                         color=Colors().blue,
                         layer=Layer.MONST_LAYER,
                         size=Size.MEDIUM)
        self.Health = Health(health=3)
        self.Attack = Attack(name='Splash',
                             damage=5,
                             alignment=Alignment.CHAOTIC)

    def death(self, entityLayer):
        '''
        Generate the explosion on death
        '''
        self.Messager.addMessage('It explodes!')
        # queue animation
        frames = {}
        frames['0'] = [
            ['','' ,''],
            ['','*',''],
            ['','' ,'']
        ]
        frames['1'] = [
            ['/' ,'-', '\\'],
            ['|',' ' ,'|'],
            ['\\' ,'-', '/']
        ]
        apos = [0,0]
        apos[0] = self.pos[0]-1
        apos[1] = self.pos[1]-1
        animation = Animation(apos, frames, Colors().blue)
        animator = Animator()
        animator.queueUp(animation)
        # spread damage
        entities = []
        points = getOneLayerPts(self.pos)
        for point in points:
            row = point[0]
            col = point[1]
            if (row,col) == self.pos:
                continue
            if self.validBounds(entityLayer, row, col):
                for entity in entityLayer[row][col]:
                    if self.attackable(entity):
                        damage = self.Attack.damage
                        kill = self.dealDamage(entityLayer,
                                               entity, damage, nomsg=True)
                        if kill:
                            entities.append(kill)
        return entities

class Newt(Entity):
    '''
    Newt Entity
    '''
    def __init__(self):
        super().__init__(name='Newt',
                         glyph='n',
                         color=Colors().yellow,
                         layer=Layer.MONST_LAYER,
                         size=Size.MEDIUM)
        self.Health = Health(health=3)
        self.Attack = Attack(name='Bite',
                             damage=1,
                             alignment=Alignment.CHAOTIC)
        self.Brain = Brain(sightRange=5, blockingLayer=Layer.MONST_LAYER)

    def input(self, energy, entityLayer, playerPos, playerZ, *args):
        '''
        Uses brain to select an action
        '''
        if energy > 0:
            return self.doAction(
                    self.Brain.input(self.pos,
                                     self.z,
                                     playerPos,
                                     playerZ,
                                     entityLayer),
                    entityLayer
                )
