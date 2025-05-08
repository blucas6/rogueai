import random
from logger import Logger

class GeneticManager:
    def __init__(self):
        self.botAmount = 50
        self.allBots = []
        self.mutation = 10
        self.actionLength = 50
        self.Logger = Logger()
        self.currentBot = 0
        self.winFile = 'win.log'
        self.mode = 'discover'
        self.iterations = 0
        if self.mode == 'discover':
            for b in range(self.botAmount):
                self.allBots.append(GeneticBot(
                    id=b,
                    mutation=self.mutation,
                    actionLength=self.actionLength
                ))
                self.Logger.log(f'BOT  {b}: {self.allBots[b].actionSequence}')
        elif self.mode == 'solver':
            with open (self.winFile, 'r+') as wf:
                actionSequence = wf.readlines()
            if actionSequence:
                self.Logger.log(f'Loading win sequence: {actionSequence}')
                self.allBots[GeneticBot(
                    id=0,
                    mutation=0,
                    actionLength=self.actionLength,
                    actionSequence=actionSequence
                )]
            else:
                self.Logger.log('Solution has not been found!')
    
    def play(self, turns, score, won):
        if self.currentBot < len(self.allBots):
            bot = self.getCurrentBot()
            bot.score = score if bot.score < score else bot.score
            action = self.getCurrentBot().pickAction(won)
            if action == 'r':
                self.Logger.log(f'BOT   {self.currentBot}: {bot.actionSequence[:bot.turn]} Z:{bot.score} W:{bot.won}')
                self.currentBot += 1
            return action
        else:
            self.cullBots()
            self.iterations += 1
            self.currentBot = 0
            return 'r'
    
    def getCurrentBot(self):
        return self.allBots[self.currentBot]

    def cullBots(self):
        self.Logger.log(f'Culling all bots: {self.iterations}')
        king = self.allBots[0]
        for idx,bot in enumerate(self.allBots):
            if not king.won and bot.won:
                # no winner yet
                king = bot
            elif king.won and bot.won and king.turn < bot.turn:
                # won in less turns
                king = bot
            elif king.score < bot.score:
                # got the highest
                king = bot
        self.Logger.log(f'King  {king.id}: {king.actionSequence[:king.turn]}')
        self.allBots = []
        for b in range(self.botAmount):
            self.allBots.append(
                GeneticBot(
                    id=b,
                    mutation=self.mutation,
                    actionLength=self.actionLength,
                    actionSequence=king.actionSequence
                ))

class GeneticBot:
    def __init__(self, id, mutation=50, actionLength=1000, actionSequence=''):
        self.id = id
        self.actions = ['1','2','3','4','6','7','8','9','<','>']
        self.actionSequence = actionSequence
        self.actionLength = actionLength
        self.won = False
        if not self.actionSequence:
            for a in range(actionLength):
                self.actionSequence += self.randomAction()
        self.turn = 0
        self.mutation = mutation
        self.score = 0

    def randomAction(self):
        return self.actions[random.randint(0,len(self.actions)-1)]

    def pickAction(self, won):
        if won:
            self.won = True
            action = 'r'
        elif self.turn < self.actionLength:
            action = self.actionSequence[self.turn]
            if random.randint(1,100) <= self.mutation:
                action = self.randomAction()
                save = self.actionSequence
                self.actionSequence = save[:self.turn] + action
                if self.turn+1 < self.actionLength:
                    self.actionSequence += save[self.turn+1:]
            self.turn += 1
        else:
            action = 'r'
        return action
