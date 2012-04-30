__metaclass__ = type

from chaofeng.ascii import *
from chaofeng.g import _w,_u
from chaofeng import Frame

class TextEditor(Frame):

    def initialize(self,text='',limit=23):
        self.buf = [ list(x) for x in text.split('\r\n')]
        self.now = self.buf[len(self.buf)-1]
        self.write(text)

    def fetch(self):
        return '\r\n'.join( ''.join(g) for g in ( ''.join(g) for g in self.buf ))

    def get(self,data):
        print repr(data)
        if data in ['\r','\n','\r\n'] :
            self.now = []
            self.buf.append(self.now)
            self.write('\r\n')
        elif data == k_del :
            if self.now :
                self.now.pop()
                self.write(backspace)
            elif len(self.buf)>1 :
                self.buf.pop()
                self.now = self.buf[len(self.buf)-1]
                self.write(movey_p)
                if len(self.now) : self.write(movex(len(self.now)))
        elif data == k_ctrl_l :
            self.write(clear + self.fetch())
        elif data in printable or ( data[0] > k_del and data[0] != IAC) :
            data = _u(data)
            self.now.append(data)
            self.write(data)
