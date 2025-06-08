import time

class Timing:
    '''Timing object'''
    _instance = None

    def __new__(obj):
        if not obj._instance:
            obj._instance = super(Timing, obj).__new__(obj)
            obj._instance.init()
        return obj._instance

    def init(self):
        self.measurements = {}
        '''Holds all measurements'''
        self.logfile = 'time.log'
        '''Log file'''
        self.currentName = ''
        '''Current measurement name being taken'''
        self.current = []
        '''Holds start and end time'''
        self.gap = []
        '''Holds start and end time of the pause'''
        self.subtract = 0
        '''Holds an amount of time to subtract at the end'''
        self.allowTiming = True

    def start(self, name):
        '''Start the measurement'''
        if self.allowTiming:
            self.currentName = name
            self.current = [time.perf_counter()]
    
    def pause(self):
        '''Pause the measurement'''
        if self.allowTiming:
            self.gap = [time.perf_counter()]
    
    def resume(self):
        '''Resume timing of the measurement'''
        if self.allowTiming:
            self.gap.append(time.perf_counter())
            self.subtract += self.gap[1] - self.gap[0]
    
    def end(self):
        '''End the measurement and save it'''
        if self.allowTiming:
            self.current.append(time.perf_counter())
            total = self.current[1] - self.current[0] - self.subtract
            if not self.currentName in self.measurements:
                self.measurements[self.currentName] = [total]
            else:
                self.measurements[self.currentName].append(total)
            self.subtract = 0
    
    def show(self):
        '''Prints out all measurements taken'''
        if self.allowTiming:
            with open(self.logfile, 'w+') as l:
                for measurement, times in self.measurements.items():
                    if len(times) > 1:
                        avg = sum([x for x in times]) / len(times)
                        l.write(f'{measurement}\n')
                        l.write(f'  Averg: {avg} (sec)\n')
                        l.write(f'  Loops: {len(times)}\n')
                        l.write(f'  FPS:   {1/avg}\n')
                    else:
                        l.write(f'{measurement}\n')
                        l.write(f'  Time: {times[0]} (sec)\n')
                        l.write(f'  FPS:  {1/times[0]}\n')

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
        self.debugOn = True
        if self.debugOn:
            self.logfile = 'log.log'
            with open(self.logfile, 'w+') as l:
                l.write('')

    def log(self, msg):
        '''
        Log a message
        '''
        if self.debugOn:
            with open(self.logfile, 'a+') as l:
                l.write(f'{msg}\n')