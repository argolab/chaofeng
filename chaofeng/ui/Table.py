import chaofeng.ascii as ac
from baseui import BaseUI

class DataLoader:

    def get(self, start, limit):
        data = self.get_raw(start, limit)
        l = len(data)
        if l < limit:
            data.extend(['']*(limit-l))
        return data

    def get_raw(self, start, limit):
        raise NotImplementedError

    def format(self, data):
        raise NotImplementedError

class PagedTable(BaseUI):

    def __init__(self, start_line=0, page_limit=20):
        self.start_line = start_line
        self.page_limit = page_limit

    def init(self, default, data_loader):
        (self.page, self.op) = divmod(default, page_limit)
        self.data_loader = data_loader
        self.data = []
        
    def fetch(self):
        return self.data[self.op]

    @property
    def hover(self):
        return (self.page * self.page_limit) + self.op

    def refresh(self):
        self.data = self.data_loader.get(self.page, self.page_limit)
        buf = [ac.move2(self.start_line, 1)]
        buf.extend(map(self.data_loader.format,
                       self.data))
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
        self.refresh()

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
