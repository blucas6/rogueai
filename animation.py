from colors import Colors
import time

class Animation:
    def __init__(self, pos, frames: dict, color: Colors, delay=0.1):
        self.pos = pos
        self.frames = frames
        self.color = color
        self.delay = delay
        self.currentFrame = 1

    def popFrame(self):
        if str(self.currentFrame) in self.frames:
            frame = self.frames[str(self.currentFrame)]
            self.currentFrame += 1
            return frame
        else:
            return None

class Animator:
    '''
    Queues animations
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
        self.AnimationQueue.append(animation)
    
    def clearQueue(self):
        self.AnimationQueue = []