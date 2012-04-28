from chaofeng.ascii import *
from chaofeng import launch,sleep

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
        data =  ( ((x,y),value,[keymap]),[...] )
        '''
        BaseUI.__init__(self,frame)
        self.data = data
        self.select = default_ord
        self.frame = frame
        self.keymap = dict( (x[1][2],x[0]) for x in filter(lambda x:len(x[1])>2,enumerate(data)))
        self.frame.write(move2(*self.data[self.select][0])+'>')
        self.height = height

    def fetch(self):
        return self.data[self.select][1]

    def send(self,data):
        if data == k_down :
            if self.select+1 < len(self.data):
                self.select += 1
        elif data == k_up :
            if self.select > 0 :
                self.select -= 1
        elif data in self.keymap :
            self.select = self.keymap[data]
        elif data == k_right :
            if not self.height : return True
            next_s = self.select + self.height
            if next_s < len(self.data):
                self.select = next_s
            else :
                return True
        elif data == k_left :
            next_s = self.select - self.height
            if next_s >= 0 :
                self.select = next_s
        else : return
        self.frame.write(backspace*2+move2(*self.data[self.select][0])+'>')

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
