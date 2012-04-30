__metaclass__ = type

from chaofeng.ascii import *
from chaofeng.g import _w,_u
from chaofeng import Frame

class Table(Frame):

    kmap = {}

    def initialize(self,format_str,line=0,data=[],default_ord=0,limit=20):
        self.format = ' '+ format_str
        self.hover = default_ord
        self.limit = limit
        self.line = line
        self.data = data
        self.refresh()

    def fetch(self):
        return self.hover

    def get(self,data):
        if data in self.kmap :
            self.kmap[data](self)

    def refresh(self):
        buf = []
        pos = self.hover % self.limit
        start = self.hover - pos
        l = len(self.data)
        m = start + self.limit
        for index in range(start,min(l,m)):
            buf.append(_w(self.format,self.data[index]))
        if l<m :
            buf.extend([kill_line]*(m-l))
        self.start = start
        self.write(move2(self.line,0))
        self.write(u'\r\n'.join(buf))
        self.write(move2(self.line+pos,0)+'>')
    kmap[k_ctrl_l] = refresh

    def goto_last(self):
        self.hover = len(self.data)-1
        self.refresh()
    kmap[k_end] = goto_last

    def move_down(self):
        if self.hover + 1 < len(self.data) :
            self.hover += 1
            if self.hover >= self.start + self.limit :
                self.refresh()
            else:
                self.write(backspace*2+movey_n+'\r>')
    kmap[k_down] = move_down

    def move_up(self):
        if self.hover > 0 :
            self.hover -= 1
            if self.hover < self.start :
                self.refresh()
            else:
                self.write(backspace*2+movey_p+'\r>')
    kmap[k_up] = move_up

    def page_down(self):
        self.hover += self.limit
        l = len(self.data)
        if self.hover >= l : self.hover = l-1
        self.refresh()
    kmap[k_page_down] = page_down

    def page_up(self):
        self.hover -= self.limit
        if self.hover < 0 :
            self.hover = 0
        self.refresh()
    kmap[k_page_up] = page_up

    def goto_first(self):
        self.hover = 0
        self.refresh()
    kmap[k_home] = goto_first
