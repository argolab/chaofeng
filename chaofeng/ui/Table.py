import chaofeng.ascii as ac
from baseui import BaseUI

class BaseTable(BaseUI):

    def __init__(self,start_line=0,limit=20):
        self.start_line = start_line
        self.limit = limit

    def init(self,format_str,data,default=0,refresh=True):
        self.format = ' ' + format_str
        self.data = data
        self.hover = default
        if refresh :
            self.refresh()

    def fetch(self):
        return self.hover

    def refresh(self):
        buf = []
        pos = self.hover % self.limit
        start = self.hover - pos
        l = len(self.data)
        m = start + self.limit
        for index in range(start,min(l,m)) :
            buf.append(self.frame.fm(self.format,self.data[index]))
        if l<m :
            buf.extend([ac.kill_line]*(m-l))
        self.start = start
        self.frame.write(ac.move2(self.start_line,0))
        self.frame.write(u'\r\n'.join(buf))
        self.frame.write(ac.move2(self.start_line+pos,0)+'>')

    def refresh_cursor(self):
        pos = self.hover % self.limit
        self.write(ac.move2(self.start_line + pos,0) + '>')

    def goto(self,which):
        self.hover = min(max(which,0),len(self.data)-1)
        self.refresh()

    def goto_offset(self,offset):
        self.hover = min(max(self.hover + offset,0),len(self.data)-1)
        self.refresh()

class SimpleTable(BaseTable):

    key_maps = {
        ac.k_up : "move_up",
        ac.k_down : "move_down",
        ac.k_page_down : "page_down",
        ac.k_page_up : "page_up",
        ac.k_home : "go_first",
        ac.k_end : "go_last",
        }
    
    def send(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()

    def move_down(self):
        self.goto_offset(1)

    def move_up(self):
        self.goto_offset(-1)

    def page_down(self):
        self.goto_offset(self.limit)
        
    def page_up(self):
        self.goto_offset(-self.limit)

    def go_first(self):
        self.goto(0)

    def go_last(self):
        self.goto(len(data))
