import chaofeng.ascii as ac
from baseui import BaseUI

class BaseTable(BaseUI):

    def __init__(self,start_line=0,limit=20):
        self.start_line = start_line
        self.limit = limit

    def init(self,getdata=None,fformat=None,default=0,refresh=False):
        self.max = 0
        self.setup(getdata,fformat,default,refresh)
        
    def setup(self,getdata=None,fformat=None,default=None,refresh=True):
        if getdata is not None:
            self.getdata = getdata
        if fformat is not None:
            self.fformat = fformat
        if default is not None:
            self.default = default
            self.hover = default
        if refresh is True:
            self.refresh()

    def fetch(self):
        return self.data[self.hover]

    def refresh(self):
        if self.hover < 0 :
            return
        pos = self.hover % self.limit
        start = self.hover - pos
        self.data = self.getdata(start,self.limit)
        buf = map(self.fformat, self.data)
        l = len(buf)
        if l < self.limit :
            buf.extend([ac.kill_line]*(self.limit -l))
        self.max = start + l - 1
        self.start = start
        self.frame.write(ac.move2(self.start_line,0))
        self.frame.write(u'\r\n'.join(buf))
        self.frame.write(ac.move2(self.start_line+pos,0)+'>')

    def refresh_cursor(self):
        pos = self.hover % self.limit
        self.frame.write(ac.move2(self.start_line + pos,0) + '>')

    def goto(self,which):
        self.hover = min(max(which,0),self.max)
        self.refresh()

    def goto_offset(self,offset):
        self.hover = min(max(self.hover + offset,0),self.max)
        self.refresh()

class SimpleTable(BaseTable):

    key_maps = {
        ac.k_up : "move_up",
        ac.k_down : "move_down",
        ac.k_page_down : "page_down",
        ac.k_page_up : "page_up",
        ac.k_home : "go_first",
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
