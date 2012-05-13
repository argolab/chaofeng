from baseui import BaseUI
import chaofeng.ascii as ac
from chaofeng import sleep
from eventlet import spawn as lanuch

class BaseTextBox(BaseUI):
    pass

class Animation(BaseTextBox):
    '''
    Call back self.frame.play_done wher playone is True.
    '''
    def __init__(self,data=None,start_line=0):
        if data :
            self.data = data
            self.len = len(self.data)
        self.start_line = start_line
        
    def init(self,data=None,auto_play=False,playone=False):
        if data :
            self.data = data
            self.len = len(self.data)
        self.select = -1
        self.playone = playone
        if auto_play :
            self.send(None)

    def clear(self):
        if hasattr(self,'thread') :
            self.thread.kill()

    def next(self):
        self.select += 1
        if self.select >= self.len :
            if self.playone :
                self.frame.play_done()
            self.select = 0

    def send(self,data):
        s = self.start_line
        while True :
            self.next()
            data,time = self.data[self.select]
            self.frame.write(ac.save+ac.move2(s,0)+data+ac.restore)
            if time == 0 :
                break
            else:
                sleep(time)

    def run(self):
        while True :
            self.send(None)

    def lanuch(self):
        self.next()
        data,time = self.data[self.select]
        self.frame.write(ac.move2(self.start_line,0)+data)
        self.thread = lanuch(self.run)

class SingleTextBox(BaseTextBox):

    def __init__(self,text,start_line=None):
        if start_line is None :
            self.text = text
        else :
            self.text = ac.move2(start_line,0) + text
        
    def init(self):
        pass

    def show(self):
        self.frame.write(self.text)
        self.frame.pause()
        self.frame.refresh()
