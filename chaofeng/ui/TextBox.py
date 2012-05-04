__metaclass__ = type

from chaofeng.ascii import *
from chaofeng.g import _w,_u
from chaofeng import BindFrame

class TextBox(BindFrame):

    shotcuts = {}

    def initialize(self,buf,limit=23):
        self._buf = buf.split('\r\n')
        self._len = len(self._buf)
        self._limit = limit
        self._start = 0
        self.goto_line(0)

    def fetch(self):
        pass

    def goto_line(self,num):
        self._start = num
        self.write(move0+clear1+'\r\n'.join(self._buf[num:num+self._limit])+move2(24,1))

    def do_up_line(self):
        if self._start == 0 : return 
        self._start -= 1
        self.write(move2(1,1)+insert1+self._buf[self._start]+move2(24,1)+kill_line)
    
    def do_down_line(self):
        if self._start + self._limit >= self.len : return
        self.write(kill_line+self._buf[self._start+self._limit]+'\r\n')
        self._start += 1
    
    def do_page_up(self):
        pass
    
    def do_page_down(self):
        pass

    def do_goto_first():
        pass

    def do_goto_last():
        pass

