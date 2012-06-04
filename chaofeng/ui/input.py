from baseui import BaseUI

class BaseInput(BaseUI):

    key_maps = {
        ac.k_del : "delete",
        ac.k_backspace : "delete",
        }
    
    def __init__(self,buffer_size=80):
        self.buffer_size = buffer_size

    def init(self):
        self.buffer = []

    def fetch(self):
        return ''.join(self.buffer)

    def acceptable(self,data):
        return True

    def push(self,data):
        self.buffer.append(data)

    def send(self,data):
        if data in key_maps :
            getattr(self,data)()
        if len(self.buffer) < self.buffer_size and acceptable(data) :
            self.push(data)

    def delete(self):
        if self.buffer :
            self.buffer.pop()
            self.write(ac.backspace)

    def read(self,prompt=None,termitor=ac.ks_finish):
        if prompt :
            self.write(prompt)
        while True :
            data = self.frame.read()
            if data in termitor :
                break
            self.send(data)
        return self.fetch()

class TextInput(BaseInput):

    def send(self,data):
        if data in key_maps :
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

class Password(BaseInput):

    def push(self,data):
        super(Password,self).push(data)
        self.frame.write('*')

    def acceptable(self,data):
        return data.isalnum()

class DatePicker(BaseInput):

    def __init__(self):
        super(DatePicker,self).__init__(8)

    def fetch(self):
        try:
            b = self.buffer
            return data(int(''.join(b[0:4])),
                        int(''.join(b[4:6])),
                        int(''.join(b[6:8])))
        except:
            return None

    def send(self,data):
        super(DatePicker,self).send(data)
        l = len(self.buffer)
        if l == 4 or l == 6 :
            self.framw.write('-')

    def delete(self):
        l = len(self.buffer)
        if l == 4 or l == 6 :
            self.frame.write(ac.backspace)
        super(DatePicker,self).delete(data)
