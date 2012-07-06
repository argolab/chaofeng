import chaofeng.ascii as ac
from baseui import BaseUI

class BaseTable(BaseUI):

    def __init__(self,start_line=0,height=20):
        self.start_line = start_line
        self.height = height

    def init(self,data_loader):
        pass

    def fetch(self):
        return self.s + self.hover

    def set_lbound(self,lower):
        pass

    def set_ubound(self,upper):
        pass

class BaseTable(BaseUI):

    def __init__(self,start_line=0,limit=20):
        self.start_line = start_line
        self.limit = limit

    def init(self,default=0):
        self.s = 0
        self.max = None
        self.hover = default
        self.default = default

    def set_fun(self,getdata=None,fformat=None,refresh=True):
        if getdata:
            self.getdata = getdata
        if fformat:
            self.fformat = fformat
        if refresh:
            self.goto(self.default)

    def fetch(self):
        return self.data and self.data[self.hover-self.s]

    def refresh(self,data=None):
        if data is None:
            data = self.getdata(self.s, self.limit)
        buf = map(self.fformat, data)
        l = len(buf)
        if l < self.limit:
            buf.extend(['']*(self.limit -l))
        self.data = data
        self.frame.write(ac.move2(self.start_line,1)+ac.kill_line)
        self.frame.write(('\r\n'+ac.kill_line).join(buf))
        self.refresh_cursor()

    def refresh_cursor(self):
        pos = self.hover % self.limit
        self.frame.write(ac.movex_d + ' ' +
                         ac.move2(self.start_line + pos,1) + '>')

    def goto(self, n):
        if n < 0 :
            n = 0
        pos = n % self.limit
        s = n - pos
        print '%s:%s %s' %(s,self.s,self.max)
        if s == self.s and self.max is not None:
            self.hover = min(n,self.max)
            self.refresh_cursor()
            return
        data = self.getdata(s, self.limit)
        l = len(data)
        if not l :
            return
        self.data = data
        self.max = s + l -1
        if n > self.max:
            n = self.max
        self.hover = n
        self.s = s
        self.refresh(data=data)

    def goto_offset(self,n):
        self.goto(self.hover + n)

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
        self.goto(self.hover+1)

    def move_up(self):
        self.goto(self.hover-1)

    def page_down(self):
        self.goto(self.hover+self.limit)
        
    def page_up(self):
        self.goto(self.hover-self.limit)

    def go_first(self):
        self.goto(0)
