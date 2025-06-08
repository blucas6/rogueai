from color import Colors
import time

class Animation:
    '''
    Default animation class, used in Animator queue
    '''
    def __init__(self, pos, frames: dict, color: Colors, delay=0.1):
        self.pos = pos
        '''position of the animation relative to the map'''
        self.frames = frames
        '''dictionary of an array of frames to display'''
        self.color = color
        '''color of the animation'''
        self.delay = delay
        '''delay between frames (engine will sleep)'''

class Animator:
    '''
    Holds the animation queue
    '''
    _instance = None
    
    def __new__(obj):
        if not obj._instance:
            obj._instance = super().__new__(obj)
            obj._instance._initialized = False
        return obj._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.AnimationQueue = []

    def queueUp(self, animation: Animation):
        '''
        Queue an animation object to be displayed
        '''
        self.AnimationQueue.append(animation)
    
    def clearQueue(self):
        '''
        Clears the animation queue
        '''
        self.AnimationQueue = []