

class Logger:
    '''
    Singleton class to log all information to the same location
    '''
    _instance = None

    def __new__(obj):
        if not obj._instance:
            obj._instance = super(Logger, obj).__new__(obj)
            obj._instance.init()
        return obj._instance

    def init(self):
        '''
        Clear the log file
        '''
        self.logfile = 'log.log'
        with open(self.logfile, 'w+') as l:
            l.write('')

    def log(self, msg):
        '''
        Log a message
        '''
        with open(self.logfile, 'a+') as l:
            l.write(f'{msg}\n')