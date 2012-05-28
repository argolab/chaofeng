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
        self.data = data
        if data :
            self.len = len(self.data)
        else : self.len = 0
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

class LongTextBox(BaseTextBox):

    key_maps = {
        ac.k_down : "move_down",
        ac.k_up : "move_up",
        }

    def __init__(self,limit=24):
        self.limit = limit
        
    def init(self,text):
        self.buf = text.split('\r\n')
        self.len = len(self.buf)
        self.goto_line(0)

    def goto_line(self,num):
        self.start = num
        self.frame.write(ac.move0 + ac.clear1 +
                         '\r\n'.join(self.buf[num:num+self.limit]) +
                         ac.move2(24,1))

    def send(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

    def handle_last(self):
        pass

    def handle_finish(self):
        raise NotImplementedError

    def move_up(self):
        if self.start == 0 :
            return
        self.start -= 1
        self.frame.write(ac.move0 + ac.insert1 + self.buf[self.start])
        self.handle_last()
        
    def move_down(self):
        if self.start + self.limit >= self.len :
            self.handle_finish()
        self.frame.write(ac.kill_line + self.buf[self.start+self.limit]+'\r\n')
        self.start += 1
