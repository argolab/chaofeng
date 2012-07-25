from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import date
from collections import deque
import datetime

class BaseInput(BaseUI):

    '''
    Base Inputer for input text.
    Will not print any thing during it run.
    '''

    key_maps = {
        ac.k_del : "delete",
        ac.k_backspace : "delete",
        }

    def init(self, buffer_size=78):
        self.buffer_size = buffer_size

    def set_buf(self, buf):
        if buf is None:
            self.buffer = deque(maxlen=self.buffer_size)
        else:
            self.buffer = deque(buf,maxlen=self.buffer_size)

    def restore_screen(self):
        self.frame.write(''.join(self.buffer))

    def do_command(self, command):
        if command :
            getattr(self, command)()

    def real_read(self):
        return self.frame.read()

    def fetch_str(self):
        return ''.join(self.buffer)

    fetch = fetch_str

    def insert_char(self, data):
        self.buffer.append(data)

    def push(self, char):
        cmd = self.key_maps.get(char)
        if cmd :
            self.do_command(cmd)
        elif self.acceptable(char):
            self.insert_char(char)

    def acceptable(self, data):  ##################### Need to reload.
        return True
            
    def read(self, buf, prompt, termitor):
        if prompt:
            self.frame.write(prompt)
        buf = buf or []
        self.set_buf(buf)
        while True:
            char = self.real_read()
            if char in termitor:
                return self.fetch()
            self.push(char)

    def delete(self):
        if self.buffer :
            return self.buffer.pop()

class VisableInput(BaseInput):

    def restore_screen(self):
        self.frame.write(''.join(self.buffer))

    def insert_char(self, data):
        super(VisableInput, self).insert_char(data)
        self.frame.write(data)
        
    def acceptable(self,data):
        return data.isalnum()

    def delete(self):
        data = super(VisableInput, self).delete()
        if data :
            self.frame.write(ac.backspace)
            return data

    def read(self, buf=None, prompt=None, termitor=ac.ks_finish):
        return super(VisableInput, self).read(buf, prompt, termitor)

    def readln(self, buf=None, prompt=None, termitor=ac.ks_finish):
        res = super(VisableInput, self).read(buf, prompt, termitor)
        self.frame.write('\r\n')
        return res
    
class EastAsiaTextInput(VisableInput):

    def acceptable(self, u_data):
        return ac.is_safe_char(u_data)

    def delete(self):
        data = super(VisableInput, self).delete() # !!! ugly but important
        if data :
            print ac.srcwidth(data)
            self.frame.write(ac.srcwidth(data) * ac.backspace)
            return data
    
class Password(BaseInput):

    def insert_char(self, data):
        super(Password, self).insert_char(data)
        self.frame.write('*')

    def acceptable(self,data):
        return data.isalnum()

    def delete(self):
        data = super(Password, self).delete()
        if data :
            self.frame.write(ac.backspace)
            return data
    
    def read(self, prompt=None, termitor=ac.ks_finish):
        return super(Password, self).read(None, prompt=prompt, termitor=termitor)

    def readln(self, prompt=None):
        res = super(Password, self).read(None, prompt=prompt, termitor=ac.ks_finish)
        self.frame.write('\r\n')
        return res

class DatePicker(BaseInput):

    str_format = '%Y-%m-%d'
    seq_bit = set((3,6))

    def init(self):
        super(DatePicker,self).init(10)

    def acceptable(self, data):
        return u'0'<= data <= '9'

    def insert_char(self, data):
        l = len(self.buffer)
        if  l <= 9 :
            super(DatePicker, self).insert_char(data)
            self.frame.write(data)
            if l in self.seq_bit:
                super(DatePicker, self).insert_char('-')
                self.frame.write('-')

    def restore_screen(self):
        self.frame.write(self.fetch_str())

    def fetch_str(self):
        return ''.join(self.buffer)

    def fetch(self):
        try:
            return datetime.datetime.strptime(self.fetch_str(),
                                              self.str_format).date()
        except ValueError:
            return None

    def read(self, prompt=None, buf=None, termitor=ac.ks_finish):
        return super(DatePicker, self).read(buf, prompt, termitor=termitor)

    def readln(self, prompt=None, buf=None):
        res = super(DatePicker, self).read(buf, prompt, termitor=ac.ks_finish)
        self.write('\r\n')
        return res

    def delete(self):
        data = super(DatePicker, self).delete()
        if data:
            self.frame.write(ac.backspace)
            return data

class ColMenu(BaseUI):

    key_maps = {
        ac.k_down : "move_down",
        ac.k_up : "move_up",
        ac.k_left : "move_left",
        ac.k_right : "move_right",
        }

    def init(self):
        self.shortcuts = {}
        self.pos = []
        self.values = []
        self.height = False

    def setup(self,data=None,height=None,background='',hover=0):
        if hover is not None:
            self.hover = hover
        if background is not None:
            self.background = background
        if height is not None:
            self.height = height
        if data is not None:
            self.set_data(*data)

    def set_data(self,values,pos,shortcuts,outlook):
        self.values = values
        self.pos = pos
        self.shortcuts = shortcuts
        self.content = self.background + outlook
        self.len = len(self.values)

    def set_content(self,content):
        self.content = content

    @staticmethod
    def tidy_data(data):
        shortcuts = {}
        pos = []
        values = []
        buf = []
        for index,item in enumerate(data) :
            if len(item) == 4 :
                text,value,key,(x,y) = item
            else :
                text,value,key = item
                x += 1
            buf.append(ac.move2(x,y+2)+text)
            shortcuts[key] = index
            pos.append((x,y))
            values.append(value)
        return (values,pos,shortcuts,''.join(buf))
        
    def fetch(self):
        return self.values[self.hover]

    def restore(self):
        self.frame.write(self.content)
        self.frame.write(ac.move2(*self.pos[self.hover])+'>')

    def refresh_cursor(self):
        self.frame.write(ac.backspace+' '+ac.move2(*self.pos[self.hover])+'>')

    def refresh_cursor_gently(self):
        self.frame.write((ac.move2(self.pos[self.hover][0], self.pos[self.hover][1]+1)))

    def send_shortcuts(self,data):
        if data in self.shortcuts :
            self.move_to(self.shortcuts[data])

    def send(self,data):
        if data in self.key_maps and hasattr(self,self.key_maps[data]) :
            getattr(self,self.key_maps[data])()
        if data in self.shortcuts :
            self.move_to(self.shortcuts[data])

    def move_down(self):
        if self.hover + 1 < self.len :
            self.hover += 1
        self.refresh_cursor()

    def move_up(self):
        if self.hover > 0 :
            self.hover -= 1
        self.refresh_cursor()

    def move_left(self):
        if self.height :
            next_s = self.hover - self.height
            if next_s >= 0 :
                self.hover = next_s
                self.refresh_cursor()
                return True

    def move_right(self):
        if self.height :
            next_s = self.hover + self.height
            if next_s < self.len :
                self.hover = next_s
                self.refresh_cursor()
                return True

    def move_to(self,which):
        self.hover = which
        self.refresh_cursor()

class Form(BaseUI):

    '''
    inputer :: (name, instance)
    inputers :: [ inputer1, inputer2 ... ]
    '''

    def init(self, buf, inputers, sl, sr):
        self.inputers = inputers
        self.buffer = buf
        for b,i in zip(self.buffer, inputers):
            i.set_buf(b)
        self.sr = sr
        self.sl = sl
        self.hover = 0

    def _fix_cursor(self):
        self.frame.write(ac.move2(self.sl+self.hover, self.sr))
        self.inputers[self.hover].restore_screen()

    def restore_screen(self):
        for i in range(len(self.inputers) - 1, -1, -1):
            self.hover = i
            self._fix_cursor()
        
    def read(self):
        max_hover = len(self.inputers) - 1
        self._fix_cursor()
        while True:
            char = self.real_read()
            if char in ac.ks_finish :
                if self.hover < max_hover:
                    self.hover += 1
                    self._fix_cursor()
                    continue
                else:
                    return self.get_status()
            if char == ac.k_ctrl_c:
                return False
            if char == ac.k_up:
                if self.hover :
                    self.hover -= 1
                self._fix_cursor()
            elif char == ac.k_down :
                self.hover = min(self.hover+1, max_hover)
                self._fix_cursor()
            else:
                self.inputers[self.hover].push(char)

    def get_status(self):
        return map(lambda x:x.fetch(), self.inputers)

    def real_read(self):
        return self.frame.read_secret()
