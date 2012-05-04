__metaclass__ = type

from chaofeng.ascii import *
from chaofeng.g import _w,_u,_d
from chaofeng import BindFrame

class Table(BindFrame):

    def initialize(self,format_str,line=0,data=[],default_ord=0,limit=20):
        self._format = ' '+ format_str
        self._hover = default_ord
        self._limit = limit
        self._line = line
        self._data = data
        self.do_refresh()

    def fetch(self):
        return self._hover

    def set_format(self,format_str):
        self._format = ' ' + format_str
        self.do_refresh()

    def do_refresh(self):
        buf = []
        pos = self._hover % self._limit
        start = self._hover - pos
        l = len(self._data)
        m = start + self._limit
        for index in range(start,min(l,m)):
            buf.append(_d(self._format,self._data[index]))
        if l<m :
            buf.extend([kill_line]*(m-l))
        self._start = start
        self.write(move2(self._line,0))
        self.write(u'\r\n'.join(buf))
        self.write(move2(self._line+pos,0)+'>')

    def do_goto_last(self):
        self._hover = len(self._data)-1
        self.refresh()

    def do_move_down(self):
        if self._hover + 1 < len(self._data) :
            self._hover += 1
            if self._hover >= self._start + self._limit :
                self.refresh()
            else:
                self.write(backspace*2+movey_n+'\r>')

    def do_move_up(self):
        if self._hover > 0 :
            self._hover -= 1
            if self._hover < self._start :
                self.refresh()
            else:
                self.write(backspace*2+movey_p+'\r>')

    def do_page_down(self):
        self._hover += self._limit
        l = len(self._data)
        if self._hover >= l : self._hover = l-1
        self.refresh()

    def do_page_up(self):
        self._hover -= self._limit
        if self._hover < 0 :
            self._hover = 0
        self.refresh()

    def do_goto_first(self):
        self._hover = 0
        self.refresh()

