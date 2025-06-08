

class Messager:
    '''
    Singleton class to write game action messages to
    '''
    _instance = None

    def __new__(obj):
        if not obj._instance:
            obj._instance = super(Messager, obj).__new__(obj)
            obj._instance.clear()
        return obj._instance
    
    def clear(self):
        '''
        Clears the msg queue
        '''
        self.MsgQueue = []

    def addMessage(self, msg: str):
        '''
        Adds a msg to the msg queue
        '''
        self.MsgQueue.append(msg)
    
    def addDamageMessage(self, nameAttack: str, nameDefend: str):
        if nameAttack == 'Player':
            self.MsgQueue.append(f'You hit the {nameDefend}')
        elif nameDefend == 'Player':
            self.MsgQueue.append(f'The {nameAttack} hits you')
        else:
            self.MsgQueue.append(f'The {nameAttack} hits the {nameDefend}')
    
    def addKillMessage(self, nameAttack: str, nameDefend: str):
        if nameAttack == 'Player':
            self.MsgQueue.append(f'You kill the {nameDefend}!')
        elif nameDefend == 'Player':
            self.MsgQueue.append(f'The {nameAttack} kills you!')
        else:
            self.MsgQueue.append(f'The {nameAttack} kills the {nameDefend}!')

    def addChargeMessage(self, nameAttack: str, nameDefend: str):
        if nameAttack == 'Player':
            self.MsgQueue.append(f'You charge the {nameDefend}')
        elif nameDefend == 'Player':
            self.MsgQueue.append(f'The {nameAttack} charges you!')
        else:
            self.MsgQueue.append(f'The {nameAttack} charges the {nameDefend}')

    def popMessage(self, blocking=True):
        '''
        If msg queue has a msg, it will return the msg by FIFO
        '''
        if self.MsgQueue:
            if blocking:
                msg = self.MsgQueue[0]
                del self.MsgQueue[0]
            else:
                msg = self.MsgQueue[0]
                self.MsgQueue = []
            return msg
        return ''