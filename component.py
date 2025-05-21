from logger import Logger
import math
from enum import Enum

class Brain:
    '''
    Brain component, if an entity needs to make decisions
    '''
    def __init__(self, sightRange):
        self.sightRange = sightRange

    def input(self, myPos, playerPos):
        distance = math.hypot(playerPos[0]-myPos[0], playerPos[1]-myPos[1])
        Logger().log(distance)
        if (distance <= self.sightRange):
            if playerPos[0] > myPos[0]:
                if playerPos[1] > myPos[1]:
                    return '3'
                elif playerPos[1] < myPos[1]:
                    return '1'
                else:
                    return '2'
            elif playerPos[0] < myPos[0]:
                if playerPos[1] > myPos[1]:
                    return '9'
                elif playerPos[1] < myPos[1]:
                    return '7'
                else:
                    return '8'
            else:
                if playerPos[1] > myPos[1]:
                    return '6'
                elif playerPos[1] < myPos[1]:
                    return '4'
        return '5'

class Health:
    '''
    Health component, if an entity needs a health bar
    '''
    def __init__(self, health):
        self.maxHealth = health
        '''Maximum for the health bar'''
        self.currentHealth = health
        '''Counter for current health'''
        self.alive = True
        '''True if health bar is above 0'''
        self.Logger = Logger()

    def changeHealth(self, amount):
        '''
        Changes the health bar by an amount
        Returns true if health change causes death
        '''
        self.currentHealth += amount
        if self.alive and self.currentHealth <= 0:
            self.alive = False
            return True
        return False
    
class Alignemnt(Enum):
    LAWFUL = 0,
    CHAOTIC = 1

class Attack:
    '''
    Attack component, if an entity can deal damage
    '''
    def __init__(self, name, damage, alignment: Alignemnt):
        self.name = name
        '''name of the attack'''
        self.damage = damage
        '''amount of damage the attack does'''
        self.alignment = alignment
        '''prevents attacking the same alignment'''