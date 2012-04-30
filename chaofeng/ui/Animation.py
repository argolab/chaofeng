__metaclass__ = type

from chaofeng import Frame
from eventlet import spawn as lanuch

class Animation(Frame):

    def initialize(self,data,start=0,run=False,background=True):
        self.data = data
        self.len = len(self.data)
        self.select = -1
        self.start = start
        if run :
            if background :
                self.thread = lanuch(self.run)
            else:
                self.run()

    def clear(self):
        self.thread.kill()

    def fetch(self):
        self.select += 1
        if self.select >= self.len : self.select = 0
        return self.data[self.select]

    def run(self):
        start = self.start
        while True:
            data,time = self.fetch()
            self.write(save+move2(start,0)+data+restore)
            sleep(time)
            
