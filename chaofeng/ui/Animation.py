__metaclass__ = type

from baseui import BaseUI
from chaofeng.ascii import *
from chaofeng import sleep
from eventlet import spawn as lanuch

class Animation(BaseUI):

    def __init__(self,data,start_line=0):
        self.data = data
        self.len = len(self.data)
        self.start_line = start_line
        
    def init(self):
        self.select = -1

    def clear(self):
        if hasattr(self,'thread') :
            self.thread.kill()

    def next(self):
        self.select += 1
        if self.select >= self.len : self.select = 0

    def run(self):
        s = self.start_line
        while True :
            self.next()
            data,time = self.data[self.select]
            self.frame.write(save+move2(s,0)+data+restore)
            sleep(time)

    def lanuch(self):
        self.next()
        data,time = self.data[self.select]
        self.frame.write(move2(self.start_line,0)+data)
        self.thread = lanuch(self.run)
