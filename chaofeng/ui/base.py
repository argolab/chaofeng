__metaclass__ = type

from chaofeng.ascii import *
from chaofeng import sleep,Frame
from chaofeng.g import _w,_u

class ColMenu(Frame):

    def initialize(self,data,default_ord=0,height=None):
        '''
        data = ( (value,keymap,[(x,y)]) ... )
        '''
        self.a = []
        self.kmap = {}
        self.pos = []
        xx = 0
        yy = 0
        for index,item in enumerate(data) :
            self.a.append(item[1])
            if item[2] : self.kmap[item[2]] = index
            if len(item) == 4 :
                xx,yy = item[3]
                height = index
            else : xx += 1
            self.write(move2(xx,yy+2) + item[0])
            self.pos.append((xx,yy))
        self.height = height
        self.s = default_ord
        self.write(move2(*self.pos[default_ord])+'>')

    def fetch(self):
        return self.a[self.s]

    def get(self,data):
        if data == k_down:
            if self.s+1 < len(self.a) : self.s += 1
        elif data == k_up:
            if self.s > 0 : self.s -= 1
        elif data == k_right :
            if not self.height : return True
            next_s = self.s + self.height
            if next_s < len(self.a):
                self.s = next_s
            else :
                return True
        elif data == k_left :
            if self.height :
                next_s = self.s - self.height
                if next_s >= 0 :
                    self.s = next_s
        elif data in self.kmap :
            self.s = self.kmap[data]
        else : return
        self.write(backspace*2+move2(*self.pos[self.s])+'>')

class TextInput(Frame):

    def initialize(self,max_len=100):
        self.buffer = []
        self.buffer_size = max_len

    def fetch(self):
        return _u(''.join(self.buffer))

    def clear(self):
        self.buffer = []

    def get(self,data):
        c = data[0]
        if c == theNULL: return
        elif data == k_backspace or data == k_del :
            if self.buffer :
                p = self.buffer.pop()
                if p >= u'\u4e00' and p <= u'\u9fa5' :
                    dd = movex(-2)
                    self.write("%s  %s" % (dd,dd))
                else:
                    dd = movex(-1)
                    self.write("%s %s" % (dd,dd))
            return
        elif ord(c) >= 32 and c != IAC:
            try:
                self.buffer.extend(list(data.decode('gbk')))
                self.write(data)
            except UnicodeDecodeError:
                pass

class Password(Frame):

    def initialize(self,max_len=100):
        self.buffer = []
        self.buffer_size = max_len

    def fetch(self):
        return _u(''.join(self.buffer))

    def clear(self):
        self.buffer = []

    def get(self,data):
        if data == k_backspace or data == k_del :
            if self.buffer :
                self.buffer.pop()
                self.write(backspace)
        elif IAC > data > print_ab :
            self.buffer.append(data)
            self.write('*')
