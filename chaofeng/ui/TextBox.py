__metaclass__ = type

from chaofeng.ascii import *
from chaofeng.g import _w,_u
from chaofeng import Frame

class TextBox(Frame):

    def initialize(self,buf,limit=23):
        self.buf = buf.split('\r\n')
        self.len = len(self.buf)
        self.limit = limit
        self.start = 0
        self.goto_line(0)

    def fetch(self):
        pass

    def goto_line(self,num):
        self.start = num
        self.write(move0+clear1+'\r\n'.join(self.buf[num:num+self.limit])+move2(24,1))

    def up_line(self):
        if self.start == 0 : return 
        self.start -= 1
        self.write(move2(1,1)+insert1+self.buf[self.start]+move2(24,1)+kill_line)
    
    def down_line(self):
        if self.start + self.limit >= self.len : return
        self.write(kill_line+self.buf[self.start+self.limit]+'\r\n')
        self.start += 1
    
    def page_up(self):
        pass
    
    def page_down(self):
        pass

    def goto_first():
        pass

    def goto_last():
        pass

    def get(self,data):
        if data == k_up :
            self.up_line()
        elif data == k_down:
            self.down_line()
        elif data == k_page_up :
            self.page_up()
        elif data == k_page_down :
            self.page_down()
        elif data == k_home :
            self.goto_first()
        elif data == k_end :
            self.goto_last()
