from entity import *
from color import Colors
from animation import Animator, Animation
from component import *
from item import *

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
        self.splashDamage = 5

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
                        damage = self.splashDamage
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
        self.Health = Health(health=3)
        self.Brain = Brain(sightRange=5, blockingLayer=Layer.MONST_LAYER)
        self.Inventory = Inventory()
        self.speed = Speed.VERY_SLOW
        self.attackSpeed = AttackSpeed.SLOW
        super().__init__(name='Newt',
                         glyph='n',
                         color=Colors().yellow,
                         layer=Layer.MONST_LAYER,
                         size=Size.MEDIUM)

    def setup(self):
        super().setup()
        self.Inventory.equip(Bite())

    def input(self, entityLayer, playerPos, playerZ, *args):
        '''
        Uses brain to select an action
        '''
        return self.doAction(
            self.Brain.input(
                self.pos,
                self.z,
                playerPos,
                playerZ,
                entityLayer
            ),
            entityLayer
        )
