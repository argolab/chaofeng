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
        ac.k_delete : u"delete",
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
        self.frame.push(u''.join(self.buffer))

    def do_command(self, command):
        if command :
            getattr(self, command)()
            self.frame.fflush()

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

    def set_acceptable(self, acceptabler):
        self.acceptable = acceptabler
            
    def read(self, buf, prompt, termitor):
        u'''
        Read a string from screen. Return the result when find a string in termitor. Return
        `False` when recv a Ctrl+c.
        '''
        if prompt:
            self.frame.push(prompt)
        buf = buf or []
        self.set_buf(buf)
        self.termitor = termitor
        while True:
            char = self.real_read()
            try:
                self.push(char)
            except TermitorInputInterrupt:
                return self.fetch()
            except SkipInputInterrupt:
                return False;

    def delete(self):
        if self.buffer :
            return self.buffer.pop()

class VisableInput(BaseInput):

    def insert_char(self, data):
        super(VisableInput, self).insert_char(data)
        self.frame.push(data)
        
    def acceptable(self,data):
        return data.isalnum()

    def delete(self):
        data = super(VisableInput, self).delete()
        if data :
            self.frame.push(ac.backspace)
            return data

    def read(self, buf=None, prompt=None, termitor=ac.ks_finish):
        return super(VisableInput, self).read(buf, prompt, termitor)

    def readln(self, buf=None, prompt=None, termitor=ac.ks_finish):
        res = super(VisableInput, self).read(buf, prompt, termitor)
        self.frame.push(u'\r\n')
        return res
    
class EastAsiaTextInput(VisableInput):

    def acceptable(self, u_data):
        return ac.is_safe_char(u_data)

    def delete(self):
        data = super(VisableInput, self).delete() # !!! ugly but important
        if data :
            self.frame.push(ac.srcwidth(data) * ac.backspace)
            return data
    
class Password(BaseInput):

    def insert_char(self, data):
        super(Password, self).insert_char(data)
        self.frame.push(u'*')

    def acceptable(self,data):
        return data.isalnum()

    def delete(self):
        data = super(Password, self).delete()
        if data :
            self.frame.push(ac.backspace)
            return data
    
    def read(self, prompt=None, termitor=ac.ks_finish):
        return super(Password, self).read(None, prompt=prompt, termitor=termitor)

    def readln(self, prompt=None):
        res = super(Password, self).read(None, prompt=prompt, termitor=ac.ks_finish)
        self.frame.push(u'\r\n')
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
            self.frame.push(data)
            if l in self.seq_bit:
                super(DatePicker, self).insert_char(u'-')
                self.frame.push(u'-')

    def restore_screen(self):
        self.frame.push(self.fetch_str())

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
        self.push(u'\r\n')
        return res

    def delete(self):
        data = super(DatePicker, self).delete()
        if data:
            self.frame.push(ac.backspace)
            return data

class ColMenu(BaseUI):

    is_destory_screen = False

    key_maps = {
        ac.k_down : u"move_down",
        ac.k_up : u"move_up",
        ac.k_left : u"move_left",
        ac.k_right : u"move_right",
        ac.k_page_up : u"goto_first",
        ac.k_page_down : u"goto_last",
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
        if len(data) == 1 :
            return [data[0][1]], [tuple(data[0][3])], {}, [data[0][0]]
        args = zip(*data)
        text, real, shortcuts = args[:3]
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

    def fetch_num(self):
        return self.hover
    
    def fetch_lastnum(self):
        return self.len - 1

    def get_real(self, hover):
        return self.real[hover]

    def restore(self):
        self.frame.push(self.background)
        self.frame.push(self.content)
        self.frame.push(ac.move2(*self.pos[self.hover])+u'>')

    def restore_cursor(self):
        self.frame.push(ac.backspace+u' '+ac.move2(*self.pos[self.hover])+u'>')

    def restore_cursor_gently(self):
        self.frame.push((ac.move2(self.pos[self.hover][0],
                                  self.pos[self.hover][1]+1)))

    def get_cursor_pos(self):
        return self.pos[self.hover][0], self.pos[self.hover][1] + 1

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
        else:
            self.hover = 0
        self.restore_cursor()

    def move_up(self):
        if self.hover > 0 :
            self.hover -= 1
        else:
            self.hover = self.len - 1
        self.restore_cursor()

    def move_left(self):
        if self.height :
            next_s = self.hover - self.height
            if next_s >= 0 :
                self.hover = next_s
                self.restore_cursor()
                return True

    def move_right(self):
        if self.height :
            next_s = self.hover + self.height
            if next_s < self.len :
                self.hover = next_s
                self.restore_cursor()
                return True

    def move_to(self,which):
        self.hover = which
        self.restore_cursor()

    def goto_first(self):
        self.hover = 0
        self.restore_cursor()

    def goto_last(self):
        self.hover = self.len - 1
        self.restore_cursor()

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
        self.frame.push(ac.clear)
        self.frame.push(self._background)
        self.frame.push(self._content)

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

# class RadioButton(BaseSelectUI):

#     hover = 0
#     start_line = 3
#     start_col = 5
    
#     u'''
#     options = [ (index, text) ... ]
#     fetch : index
#     display in form : text | <<NONE>>
#     '''

#     def init(self, options, default=None, background=u''):
#         if default is None:
#             default = 0
#         super(RadioButton, self).init(options, background=background)
        
#     def formater(self, index, op):
#         return u'%s%s %s' % (ac.move2(index + self.start_line, self.start_col),
#                             chr(index+65), op)  ## +65 to covert into Upper

#     def hook_hover(self, g):
#         print ('g', g)
#         self.hover = g
#         self.frame.write(ac.move2(g + self.start_line, self.start_col+2))

#     def restore_screen(self):
#         super(RadioButton, self).restore_screen()
#         self.frame.write(ac.move2(self.hover + self.start_line, self.start_col+2))

#     def fetch(self):
#         if self._options :
#             return self.hover
#         else:
#             return None

#     def fetch_str(self):
#         f = self.fetch()
#         if f:
#             return self._options[f][1]
#         else:
#             return u'<<NONE>>'

class Form(BaseUI):

    u'''
    data :: [( name, text, handler) ]

    handler may raise a ValueError, or return the value to save.
    '''

    def init(self, data, start_line=3, height=20, msg_line=22):
        self.data = data
        self.start_line = start_line
        self.msg_line = 20
        self.height = height

    def read(self, default=None):
        if default is None:
            default = {}
        for name,text,handler in self.data :
            self.frame.push(''.join((ac.move2(self.start_line, 1),
                                      ac.kill_line_n(self.height),
                                      ac.move2(self.start_line, 1), text)))
            while True:
                self.frame.push(''.join([ac.move2(self.start_line + self.height, 1),
                                         ac.kill_line]))
                value = self.readline(default.get(name))
                if value is False:
                    return
                try:
                    value = handler(value)
                except ValueError as e:
                    self.frame.push('%s%s\r\n' % (ac.move2(self.msg_line, 1), e.message))
                else:
                    default[name] = value
                    break
        return default

    def readline(self, prefix, acceptable=ac.is_safe_char, finish=ac.ks_finish, buf_size=78):
        '''
        Return the string when `finish` key recv, return False while recv a k_ctrl_c
        '''
        if prefix is None:
            buf = []
        else:
            buf = list(prefix)
            self.frame.push(prefix)
        while True:
            char = self.frame.read_secret()
            if char in ac.ks_delete :
                if buf :
                    data = buf.pop()
                    self.frame.push(ac.backspace * ac.srcwidth(data))
                    continue
            elif char in finish :
                return u''.join(buf)
            elif char == ac.k_ctrl_c:
                return False
            elif acceptable(char):
                if len(buf) < buf_size:
                    buf.append(char)
                    self.frame.push(char)
        return u''.join(buf)
