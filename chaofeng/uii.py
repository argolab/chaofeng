# -*- coding: utf-8 -*-

__metaclass__ = type

from chaofeng.ascii import *
from chaofeng import launch,sleep
from chaofeng.g import _w,_u

class BaseUI:

    def __init__(self,frame,**kwarg):
        self.frame = frame
        self.session = frame.session

    def fetch(self):
        pass

    def send(self,data):
        pass

    def clear(self):
        pass

    def read(self,termitor=['\r\n','\n','\r\0']):
        f = self.frame
        data = f.read()
        self.clear()
        while data not in termitor :
            if self.send(data) : break
            data = f.read()
        return self.fetch()

class ColMenu(BaseUI):

    def __init__(self,frame,data,default_ord=0,height=None):
        '''
        data = ( (value,keymap,[(x,y)]) ... )
        '''
        BaseUI.__init__(self,frame)
        self.a = []
        self.kmap = {}
        self.pos = []
        xx = 0
        yy = 0
        for index,item in enumerate(data) :
            self.a.append(item[0])
            if item[1] : self.kmap[item[1]] = index
            if len(item) == 3 :
                xx,yy = item[2]
                height = index
            else : xx += 1
            self.pos.append((xx,yy))
        self.height = height
        self.s = default_ord
        self.frame.write(move2(*self.pos[default_ord])+'>')

    def fetch(self):
        return self.a[self.s]

    def send(self,data):
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
        self.frame.write(backspace*2+move2(*self.pos[self.s])+'>')

class TextInput(BaseUI):
    
    def __init__(self,frame,max_len=100):
        BaseUI.__init__(self,frame)
        self.buffer = []
        self.buffer_size = max_len

    def fetch(self):
        return ''.join(self.buffer)

    def clear(self):
        self.buffer = []

    def send(self,data):
        c = data[0]
        if c == theNULL: return
        elif data == k_backspace or data == k_del :
            if self.buffer :
                p = self.buffer.pop()
                if p >= u'\u4e00' and p <= u'\u9fa5' :
                    dd = movex(-2)
                    self.frame.write("%s  %s" % (dd,dd))
                else:
                    dd = movex(-1)
                    self.frame.write("%s %s" % (dd,dd))
            return
        elif ord(c) >= 32 and c != IAC:
            try:
                self.buffer.extend(list(data.decode('gbk')))
                self.frame.write(data)
            except UnicodeDecodeError:
                pass

class Password(BaseUI):

    def __init__(self,frame,max_len=100):
        BaseUI.__init__(self,frame)
        self.buffer = []
        self.buffer_size = max_len

    def fetch(self):
        return ''.join(self.buffer)

    def clear(self):
        self.buffer = []

    def send(self,data):
        if data == k_backspace or data == k_del :
            if self.buffer :
                self.buffer.pop()
                self.frame.write(backspace)
        elif IAC > data > print_ab :
            self.buffer.append(data)
            self.frame.write('*')
            
class Animation(BaseUI):

    def __init__(self,frame,data,start=0):
        BaseUI.__init__(self,frame)
        self.data = data
        self.len = len(self.data)
        self.select = -1
        self.start = start

    def fetch(self):
        self.select += 1
        if self.select >= self.len : self.select = 0
        return self.data[self.select]

    def send(self,data):
        # self.frame.write(self.fetch()[0])
        pass

    def read(self):
        start = self.start
        try:
            while True :
                data,time = self.fetch()
                self.frame.write(save+move2(start,0)+data+restore)
                sleep(time)
        except None:
            print 'Alert'
            pass

    def run_bg(self):
        launch(self.read)

class Table(BaseUI):

    kmap = {}

    def __init__(self,frame,format_str,line=0,data=[],default_ord=0,limit=20):
        BaseUI.__init__(self,frame)
        self.format = ' '+ format_str
        self.hover = default_ord
        self.limit = limit
        self.line = line
        self.data = data
        self.refresh()

    def fetch(self):
        return self.hover

    def send(self,data):
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
        self.frame.write(move2(self.line,0))
        self.frame.write(u'\r\n'.join(buf))
        self.frame.write(move2(self.line+pos,0)+'>')
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
                self.frame.write(backspace*2+movey_n+'\r>')
    kmap[k_down] = move_down

    def move_up(self):
        if self.hover > 0 :
            self.hover -= 1
            if self.hover < self.start :
                self.refresh()
            else:
                self.frame.write(backspace*2+movey_p+'\r>')
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

class TextBox(BaseUI):

    def __init__(self,frame,buf,limit=23):
        super(TextBox,self).__init__(frame)
        self.buf = buf.split('\r\n')
        self.len = len(self.buf)
        self.limit = limit
        self.start = 0
        self.goto_line(0)

    def fetch(self):
        pass

    def push(self,data):
        self.frame.write(data)

    def goto_line(self,num):
        self.start = num
        self.push(move0+clear1+'\r\n'.join(self.buf[num:num+self.limit])+move2(24,1))

    def up_line(self):
        if self.start == 0 : return 
        self.start -= 1
        self.push(move2(1,1)+insert1+self.buf[self.start]+move2(24,1)+kill_line)
    
    def down_line(self):
        if self.start + self.limit >= self.len : return
        self.push(kill_line+self.buf[self.start+self.limit]+'\r\n')
        self.start += 1
    
    def page_up(self):
        pass
    
    def page_down(self):
        pass

    def goto_first():
        pass

    def goto_last():
        pass

    def send(self,data):
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

class TextEditor(BaseUI):

    def __init__(self,frame,text='',limit=23):
        super(TextEditor,self).__init__(frame)
        self.buf = [ list(x) for x in text.split('\r\n')]
        self.now = self.buf[len(self.buf)-1]
        self.frame.write(text)

    def fetch(self):
        return '\r\n'.join( ''.join(g) for g in ( ''.join(g) for g in self.buf ))

    def send(self,data):
        print repr(data)
        if data in ['\r','\n','\r\n'] :
            self.now = []
            self.buf.append(self.now)
            self.frame.write('\r\n')
        elif data == k_del :
            if self.now :
                self.now.pop()
                self.frame.write(backspace)
            elif len(self.buf)>1 :
                self.buf.pop()
                self.now = self.buf[len(self.buf)-1]
                self.frame.write(movey_p)
                if len(self.now) : self.frame.write(movex(len(self.now)))
        elif data == k_ctrl_l :
            self.frame.write(clear + self.fetch())
        elif data in printable or ( data[0] > k_del and data[0] != IAC) :
            data = _u(data)
            self.now.append(data)
            self.frame.write(data)