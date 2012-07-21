from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import date
from collections import deque

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
        self.buffer = deque(buf,maxlen=self.buffer_size)

    def restore_screen(self):
        pass

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

    def read(self, acceptable, buf, prompt, termitor):
        if prompt:
            self.frame.write(prompt)
        buf = buf or []
        self.set_buf(buf)
        while True:
            char = self.real_read()
            if char in termitor:
                return self.fetch()
            cmd = self.key_maps.get(char)
            if cmd :
                self.do_command(cmd)
            elif acceptable(char):
                self.insert_char(char)

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
        super(VisableInput, self).read(self.acceptable, buf, prompt, termitor)

    def readln(self, buf=None, prompt=None, termitor=ac.ks_finish):
        super(VisableInput, self).read(self.acceptable, buf, prompt, termitor)
        self.frame.write('\r\n')

class EastAsiaTextInput(VisableInput):

    def acceptable(self, u_data):
        return ac.is_safe_char(u_data)

    def delete(self):
        data = super(VisableInput, self).delete() # !!! ugly but important
        print repr(data)
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
    
    def read(self, prompt=None):
        super(Password, self).read(self.acceptable, None, prompt=prompt, termitor=ac.ks_finish)

    def readln(self, prompt=None):
        super(Password, self).read(self.acceptable, None, prompt=prompt, termitor=ac.ks_finish)
        self.frame.write('\r\n')

class DatePicker(BaseInput):

    str_format = '%Y-%m-%d'
    seq_bit = set((3,6))

    def init(self):
        super(DatePicker,self).init(10)

    def acceptable(self, data):
        print data
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

    def fetch_date(self):
        try:
            return datetime.datetime.strptime(self.fetch_str(),
                                              self.str_format).date()
        except ValueError:
            return None

    def read(self, prompt=None, buf=None):
        super(DatePicker, self).read(self.acceptable, buf, prompt, termitor=ac.ks_finish,)

    def readln(self, prompt=None, buf=None):
        super(DatePicker, self).read(self.acceptable, buf, prompt, termitor=ac.ks_finish)
        self.write('\r\n')

    def delete(self):
        data = super(DatePicker, self).delete()
        if data:
            self.frame.write(ac.backspace)
            return data

# class HiddenInput(TextInput):

#     def init(self,buffer_size=80,text='',start_line=0):
#         super(HiddenInput,self).init(buffer_size)
#         self.start_line = start_line
#         self.set_text(text)

#     def reset(self,text=None,refresh=True):
#         super(HiddenInput,self).reset()
#         self.set_text(text)
#         if refresh:
#             self.hidden()
        
#     def set_text(self,text):
#         if text :
#             self.text = text

#     def read(self,prompt=None,termitor=ac.ks_finish):
#         self.frame.write(ac.move2(self.start_line,0) + ac.kill_line)
#         if prompt :
#             self.frame.write(prompt)
#         elif hasattr(self,'prompt') :
#             self.frame.write(self.prompt)
#         self.reset(refresh=False)
#         while True :
#             data = self.frame.read_secret()
#             if data in termitor :
#                 break
#             self.send(data)
#         self.frame.write(ac.move2(self.start_line,0) +
#                          ac.kill_line + self.text)
#         return self.fetch()

#     def send_with_hook(self,data):
#         if data in self.key_maps :
#             getattr(self,self.key_maps[data])()
#         if len(self.buffer) < self.buffer_size and self.acceptable(data) :
#             self.push_with_hook(data)

#     def push_with_hook(self,data):
#         super(HiddenInput,self).push(data)
#         self.hook(''.join(self.buffer))

#     def read_with_hook(self,hook,prompt=None,termitor=ac.ks_finish):
#         self.hook = hook
#         self.frame.write(ac.save + ac.move2(self.start_line,0) + ac.kill_line)
#         if prompt :
#             self.frame.write(prompt)
#         elif hasattr(self,'prompt') :
#             self.frame.write(self.prompt)
#         self.reset(refresh=False)
#         while True :
#             data = self.frame.read_secret()
#             if data in termitor :
#                 break
#             self.send_with_hook(data)
#         self.frame.write(ac.move2(self.start_line,0) +
#                          ac.kill_line + self.text + ac.restore)
#         return self.fetch()

#     def hidden(self):
#         self.frame.write(ac.move2(self.start_line,0) + self.text)

class Form(BaseUI):

    def init(self):
        pass

    def reset(self):
        pass

    def run(self, actions, pos, acc=None):
        i = 0
        l = len(actions)
        if acc is None:
            acc = {}
        while i<l :
            self.frame.write(ac.move2(*pos[i]) + ac.kill_to_end)
            res = actions[i](acc)
            print res
            if res is True:
                i += 1
            elif res is False:
                i -= 1
        return acc
