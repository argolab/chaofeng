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

    def init(self,data=None,start_line=0):
        self.data = data
        if data :
            self.len = len(self.data)
        else : self.len = 0
        self.start_line = start_line
        
    def setup(self,data=None,auto_play=False,playone=False):
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
        if self.select+1 >= self.len :
            if self.playone :
                self.frame.play_done()
            self.select = 0
        else:
            self.select += 1

    def send(self,sp):
        s = self.start_line
        while True :
            self.next()
            data,time = self.data[self.select]
            self.frame.write(ac.save+ac.move2(s,0)+data+ac.restore)
            if time == 0 :
                self.frame.pause()
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

    def init(self,text,start_line=None):
        if start_line is None :
            self.text = text
        else :
            self.text = ac.move2(start_line,0) + text
        
    def reset(self):
        pass

    def show(self):
        self.frame.write(self.text)
        self.frame.pause()
        self.frame.refresh()

class LongTextBox(BaseTextBox):

    '''
    Widget for view long text.
    When user try move_up in first will,self.handle_finish(False)
    will be called, and self.handle_finish(True) will be when
    move_down in last lin.
    '''

    key_maps = {
        ac.k_down : "move_down",
        ac.k_up : "move_up",
        }

    def init(self,height=23):
        self.h = height
        self.buf = None
        
    def reset(self,text=None):
        if text is not None:
            self.set_text(text)

    def bind(self,callback):
        self.handle_finish = callback

    def getscreen(self):
        return '\r\n'.join(self.getlines(self.s, self.s+self.h))

    def getscreen_with_raw(self):
        buf = self.getlines(self.s, self.s+self.h)
        return ('\r\n'.join(buf), buf)

    def set_text(self,text):
        self.buf = text.splitlines()
        self.s = 0
        self.len = len(self.buf)
        self.max = max(0,self.len - self.h)
        
    def getlines(self,f,t):
        if t > self.len :
            return self.buf[f:t]+['~',]*(t-self.len)
        else:
            return self.buf[f:t]

    def set_start(self,start):
        if start == self.s:
            return
        if (self.s > start) and (self.s <= start + 10):
            offset = self.s - start
            self.write(ac.move0 + ac.insertn(offset) + '\r')
            self.write('\r\n'.join(self.getlines(start,self.s)))
            self.s = start
        elif (start > self.s) and (start <= self.s + 10):
            astart = self.s + self.h # Append Start
            self.write(ac.move2(self.h+1,0))
            self.write(ac.kill_line)
            self.write('\r\n'.join(self.getlines(astart, start + self.h)))
            self.write('\r\n')
            self.s = start
        else :
            self.s = start
            self.refresh_all()

    def move_up(self):
        if self.s :
            self.set_start(self.s-1)
        else:
            self.handle_finish(False)
            
    def move_down(self):
        if self.s + self.h < self.len:
            self.set_start(self.s+1)
        else:
            self.handle_finish(True)

    def go_line(self,num):
        if self.s == 0 and num < 0 :
            self.handle_finish(True)
        if self.s == self.max and num > 0:
            self.handle_finish(False)
        self.set_start(max(0,min(num,self.len-self.h)))
        
    def send(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

    def go_first(self):
        self.go_line(0)

    def go_last(self):
        self.go_line(self.len-self.h)

    def page_down(self):
        self.go_line(self.s - self.h)

    def page_up(self):
        self.go_line(self.s + self.h)

    def refresh_all(self):
        self.write(ac.move0 + ac.clear)
        self.write(self.getscreen())
        
    def write(self,data):
        self.frame.write(data)
