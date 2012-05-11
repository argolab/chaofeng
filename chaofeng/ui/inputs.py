from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import date

class BaseInput(BaseUI):

    key_maps = {
        ac.k_del : "delete",
        ac.k_backspace : "delete",
        }
    
    def __init__(self,buffer_size=1024,prompt=None):
        self.buffer_size = buffer_size
        if prompt :
            self.prompt = prompt

    def init(self):
        self.buffer = []

    def fetch(self):
        return ''.join(self.buffer)

    def acceptable(self,data):
        return True

    def push(self,data):
        self.buffer.append(data)

    def send(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        if len(self.buffer) < self.buffer_size and self.acceptable(data) :
            self.push(data)

    def delete(self):
        if self.buffer :
            self.buffer.pop()
            self.frame.write(ac.backspace)

    def read(self,prompt=None,termitor=ac.ks_finish):
        if prompt :
            self.frame.write(prompt)
        elif hasattr(self,'prompt') :
            self.frame.write(self.prompt)
        self.init()
        while True :
            data = self.frame.read()
            if data in termitor :
                break
            self.send(data)
        return self.fetch()

    def readln(self,prompt=None,termitor=ac.ks_finish):
        res = self.read(prompt,termitor)
        self.frame.write('\r\n')
        return res

class TextInput(BaseInput):

    def push(self,data):
        super(TextInput,self).push(data)
        self.frame.write(data)

    def acceptable(self,data):
        return data.isalnum()

class UnicodeTextInput(BaseInput):

    def send(self,data):
        if data in self.key_maps :
            getattr(self,data)()
        try:
            u_data = self.frame.u(data)
            if len(self.buffer) + len(u_data) < self.buffer_size \
                    and self.acceptable(u_data) :
                self.push(u_data)
        except : pass
        
    def push(self,u_data):
        super(TextInput,self).push(list(u_data))
        self.frame.write(u_data)

    def delete(self):
        raise NotImplementedError

    def acceptable(self,u_data):
        raise NotImplementedError

class zhTextInput(UnicodeTextInput):

    def acceptable(self,u_data):
        return u_data[0] != ac.IAC and \
            (data in ac.printable or \
            ac.is_chchar(u_data))

    def delete(self):
        if self.buffer :
            data = self.buffer.pop()
            if ac.is_chchar(data) :
                self.frame.write(ac.backspace*2)
            else : self.frame.write(ac.backspace)

class Password(BaseInput):

    def push(self,data):
        super(Password,self).push(data)
        self.frame.write('*')

    def acceptable(self,data):
        return data.isalnum()

class DatePicker(BaseInput):

    def __init__(self):
        super(DatePicker,self).__init__(8)

    def acceptable(self,data):
        return data.isdigit()

    def push(self,data):
        super(DatePicker,self).push(data)
        self.frame.write(data)

    def fetch(self):
        try:
            b = self.buffer
            return date(int(''.join(b[0:4])),
                        int(''.join(b[4:6])),
                        int(''.join(b[6:8])))
        except:
            return None

    def send(self,data):
        super(DatePicker,self).send(data)
        l = len(self.buffer)
        if l == 4 or l == 6 :
            self.frame.write('-')

    def delete(self):
        l = len(self.buffer)
        if l == 4 or l == 6 :
            self.frame.write(ac.backspace)
        super(DatePicker,self).delete()
