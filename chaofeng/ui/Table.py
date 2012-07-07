import chaofeng.ascii as ac
from baseui import BaseUI

__metaclass__ = type

class DataLoader:

    def __init__(self,get_raw,format, get_upper):
        self.get_raw = get_raw
        self.format = format
        self.get_upper = get_upper
        
    def fix_range(self,x):
        upper = self.get_upper()-1
        return min(upper,max(0,x))

    def get(self, start, limit):
        self.raw_data = self.get_raw(start, limit)
        data = map(self.format,
                   self.raw_data)
        l = len(data)
        if l < limit:
            data.extend(['']*(limit-l))
        return data

    def item(self,key):
        return self.raw_data[key]

class PagedTable(BaseUI):

    def __init__(self, start_line=0, page_limit=20):
        self.start_line = start_line
        self.page_limit = page_limit

    def init(self, default, data_loader):
        (self.page, self.op) = divmod(default, self.page_limit)
        self.data_loader = data_loader
        self.data = []
        
    def fetch(self):
        return self.data_loader.raw_data[self.op]

    @property
    def hover(self):
        return (self.page * self.page_limit) + self.op

    def restore(self):
        buf = self.data_loader.get(self.page, self.page_limit)
        self.frame.write(ac.move2(self.start_line, 1)+ac.kill_line)
        self.frame.write( ('\r\n'+ac.kill_line).join(buf))
        self.refresh_cursor()

    def _goto(self, page, op):
        if page == self.page:
            if op != self.op:
                self.op = op
                self.refresh_cursor()
            return
        self.page = self.page
        self.op = self.op
        self.restore()

    def refresh_cursor(self):
        self.frame.write(ac.movex_d + ' ' +
                         ac.move2(self.start_line + self.op,1) + '>')

    def goto(self, which):
        which = self.data_loader.fix_range(which)
        self._goto(*divmod(which, self.page_limit))

    def goto_offset(self, offset):
        self.goto( self.hover + offset)

class SimpleTable(PagedTable):

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
