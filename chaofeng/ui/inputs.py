from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import date
from collections import deque
import datetime
from uiexception import *

class SubmitInterrupt(BaseUIInterrupt):pass

class BaseInput(BaseUI):

    is_destory_screen = False
    termitor = ac.ks_finish

    u'''
    Base Inputer for input text.
    Will not print any thing during it run.
    '''

    key_maps = {
        ac.k_del : u"delete",
        ac.k_backspace : u"delete",
        }

    def init(self, buffer_size=78):
        self.buffer_size = buffer_size
            
    def set_buf(self, buf):
        if buf is None:
            self.buffer = deque(maxlen=self.buffer_size)
        else:
            self.buffer = deque(buf,maxlen=self.buffer_size)
        return self

    def restore_screen(self):
        self.frame.write(u''.join(self.buffer))

    def do_command(self, command):
        if command :
            getattr(self, command)()

    def real_read(self):
        return self.frame.read_secret()

    def fetch_str(self):
        return u''.join(self.buffer)

    fetch = fetch_str

    def insert_char(self, data):
        self.buffer.append(data)

    def push(self, char):
        if char in self.termitor:
            raise TermitorInputInterrupt
        if char == ac.k_ctrl_c:
            raise SkipInputInterrupt
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
        self.termitor = termitor
        while True:
            char = self.real_read()
            try:
                self.push(char)
            except TermitorInputInterrupt:
                break
        return self.fetch()

    def delete(self):
        if self.buffer :
            return self.buffer.pop()

class VisableInput(BaseInput):

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
        self.frame.write(u'\r\n')
        return res
    
class EastAsiaTextInput(VisableInput):

    def acceptable(self, u_data):
        return ac.is_safe_char(u_data)

    def delete(self):
        data = super(VisableInput, self).delete() # !!! ugly but important
        if data :
            self.frame.write(ac.srcwidth(data) * ac.backspace)
            return data
    
class Password(BaseInput):

    def insert_char(self, data):
        super(Password, self).insert_char(data)
        self.frame.write(u'*')

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
        self.frame.write(u'\r\n')
        return res

class DatePicker(BaseInput):

    str_format = u'%Y-%m-%d'
    seq_bit = set((3,6))

    def init(self):
        super(DatePicker,self).init(10)

    def set_from_date(self, date):
        self.set_buf(date.strftime(u"%Y-%m-%d"))
        return self

    def acceptable(self, data):
        return u'0'<= data <= u'9'

    def insert_char(self, data):
        l = len(self.buffer)
        if  l <= 9 :
            super(DatePicker, self).insert_char(data)
            self.frame.write(data)
            if l in self.seq_bit:
                super(DatePicker, self).insert_char(u'-')
                self.frame.write(u'-')

    def restore_screen(self):
        self.frame.write(self.fetch_str())

    def fetch_str(self):
        return u''.join(self.buffer)

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
        self.write(u'\r\n')
        return res

    def delete(self):
        data = super(DatePicker, self).delete()
        if data:
            self.frame.write(ac.backspace)
            return data

class ColMenu(BaseUI):

    is_destory_screen = False

    key_maps = {
        ac.k_down : u"move_down",
        ac.k_up : u"move_up",
        ac.k_left : u"move_left",
        ac.k_right : u"move_right",
        }

    def init(self):
        self.shortcuts = {}
        self.pos = {}
        self.vlaues = []
        self.text = []

    def setup(self, data, height=None, background=u'', hover=0):
        self.hover = hover
        self.background = background
        self.height = height
        self.set_data(*data)

    def set_data(self, real, pos, shortcuts, text):
        self.real = real
        self.pos = pos
        self.shortcuts = shortcuts
        self.text = text
        self.content = u''.join([ u'%s  %s' % (ac.move2(*p), t)
                                 for p,t in zip(pos, text)])
        self.len = len(self.real)

    @staticmethod
    def tidy_data(data):
        text, real, shortcuts = zip(*data)
        shortcuts = dict( (k,i) for i,k in enumerate(shortcuts))
        pos = [ d[3] if len(d)==4 else None for d in data ]
        sx,sy = 0,0
        for i in range(len(pos)):
            if pos[i] :
                sx,sy = pos[i]
            else:
                sx += 1
                pos[i] = (sx,sy)
        return real, pos, shortcuts, text
        
    def fetch(self):
        return self.real[self.hover]

    def restore(self):
        self.frame.write(self.background)
        self.frame.write(self.content)
        self.frame.write(ac.move2(*self.pos[self.hover])+u'>')

    def refresh_cursor(self):
        self.frame.write(ac.backspace+u' '+ac.move2(*self.pos[self.hover])+u'>')

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

class BaseSelectUI(BaseUI):

    is_destory_screen = True

    hover = 0

    def init(self, options, background=u''):
        self._background = background
        self._options = options
        self._len = len(options)
        self._content = u''.join([self.formater(index,d)
                                 for index,d in enumerate(self._options)])

    def formater(self, index, op):
        raise NotImplementedError

    def hook_hover(self, index):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError(self)

    def restore_screen(self):
        self.frame.write(ac.clear)
        self.frame.write(self._background)
        self.frame.write(self._content)

    def push(self, char):
        if char :
            if char == ac.k_up:
                if self.hover :
                    self.hook_hover(self.hover-1)
            elif char == ac.k_down:
                if self.hover < self._len-1:
                    self.hook_hover(self.hover+1)
            else:
                g = ord(char[0].upper()) - 65   ####### The order
                if 0 <= g < self._len :
                    self.hook_hover(g)
                elif char in ac.ks_finish :
                    raise TermitorInputInterrupt
                elif char in ac.k_ctrl_c :
                    raise SkipInputInterrupt

    def read(self):
        self.restore_screen()
        while True:
            char = self.frame.read_secret()
            try:
                self.push(char)
            except TermitorInputInterrupt:
                break
        return self.fetch()

class RadioButton(BaseSelectUI):

    hover = 0
    start_line = 3
    start_col = 5
    
    u'''
    options = [ (index, text) ... ]
    fetch : index
    display in form : text | <<NONE>>
    '''

    def init(self, options, default=None, background=u''):
        if default is None:
            default = 0
        super(RadioButton, self).init(options, background=background)
        
    def formater(self, index, op):
        return u'%s%s %s' % (ac.move2(index + self.start_line, self.start_col),
                            chr(index+65), op)  ## +65 to covert into Upper

    def hook_hover(self, g):
        print ('g', g)
        self.hover = g
        self.frame.write(ac.move2(g + self.start_line, self.start_col+2))

    def restore_screen(self):
        super(RadioButton, self).restore_screen()
        self.frame.write(ac.move2(self.hover + self.start_line, self.start_col+2))

    def fetch(self):
        if self._options :
            return self.hover
        else:
            return None

    def fetch_str(self):
        f = self.fetch()
        if f:
            return self._options[f][1]
        else:
            return u'<<NONE>>'
        
class CheckBox(BaseSelectUI):

    u'''
    options = [ (text, is_select) ... ] ,is_select :: True | False
    fetch :: a set that holds all index selected
    display in form : text,text,text... | <<NONE>>
    '''

    start_line = 3
    start_col = 5
    op_width = 30

    yes = u'Y'
    no = u'X'
    
    def init(self, options, background=u''):
        self.selected = [ x[1] for x in options]
        super(CheckBox, self).init(options, background)

    def formater(self, index, op):
        return u'%s%s %*s %s' % (ac.move2(index+self.start_line, self.start_col), 
                               chr(index+65), self.op_width, op[0],
                               self.yes if self.selected[index] else self.no)

    def hook_hover(self, index):
        self.selected[index] = not self.selected[index]
        self.frame.write( u'%s%s' % (ac.move2(index+self.start_line, self.op_width+self.start_col+3),
                                    self.yes if self.selected[index] else self.no))

    def fetch_str(self):
        s = self.fetch()
        if s :
            return u','.join(self._options[x][0] for x in s)
        else:
            return u'<<NONE>>'

    def fetch(self):
        f = filter( lambda x: self.selected[x], range(len(self.selected)))
        return set(f)
