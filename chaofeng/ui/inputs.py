from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import date

class BaseInput(BaseUI):

    key_maps = {
        ac.k_del : "delete",
        ac.k_backspace : "delete",
        }
    
    def init(self,buffer_size=1024,prompt=None):
        self.buffer_size = buffer_size
        if prompt :
            self.prompt = prompt

    def reset(self,buf=None,prompt=None):
        if prompt:
            self.prompt = prompt
        self.buffer = buf or []
        print (self.buffer, 'zz')

    def restore(self):
        self.frame.write(self.fetch_str())

    def fetch(self):
        return ''.join(self.buffer)

    fetch_str = fetch

    def acceptable(self,data):
        return True

    def push(self,data):
        if isinstance(data,list):
            self.buffer.extend(data)
        else:
            self.buffer.append(data)

    def send(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        else:
            if len(self.buffer) < self.buffer_size and self.acceptable(data) :
                self.push(data)

    def delete(self):
        if self.buffer :
            self.buffer.pop()
            self.frame.write(ac.backspace)

    def read(self, buf=None, prompt=None,termitor=ac.ks_finish, stop=set()):
        if prompt :
            self.frame.write(prompt)
        elif hasattr(self,'prompt') :
            self.frame.write(self.prompt)
        self.reset(buf=buf)
        self.restore()
        while True :
            data = self.frame.read()
            if data in stop:
                return False
            for char in data :
                if char in termitor :
                    return self.fetch()
                self.send(char)

    def readln(self,prompt=None,termitor=ac.ks_finish):
        print 5
        res = self.read(prompt=prompt,termitor=termitor)
        print 6
        self.frame.write('\r\n')
        print 7
        return res

class TextInput(BaseInput):

    def push(self,data):
        super(TextInput,self).push(data)
        self.frame.write(data)

    def acceptable(self,data):
        return data.isalnum()

class HiddenInput(TextInput):

    def init(self,buffer_size=80,text='',start_line=0):
        super(HiddenInput,self).init(buffer_size)
        self.start_line = start_line
        self.set_text(text)

    def reset(self,text=None,refresh=True):
        super(HiddenInput,self).reset()
        self.set_text(text)
        if refresh:
            self.hidden()
        
    def set_text(self,text):
        if text :
            self.text = text

    def read(self,prompt=None,termitor=ac.ks_finish):
        self.frame.write(ac.move2(self.start_line,0) + ac.kill_line)
        if prompt :
            self.frame.write(prompt)
        elif hasattr(self,'prompt') :
            self.frame.write(self.prompt)
        self.reset(refresh=False)
        while True :
            data = self.frame.read_secret()
            if data in termitor :
                break
            self.send(data)
        self.frame.write(ac.move2(self.start_line,0) +
                         ac.kill_line + self.text)
        return self.fetch()

    def send_with_hook(self,data):
        if data in self.key_maps :
            getattr(self,self.key_maps[data])()
        if len(self.buffer) < self.buffer_size and self.acceptable(data) :
            self.push_with_hook(data)

    def push_with_hook(self,data):
        super(HiddenInput,self).push(data)
        self.hook(''.join(self.buffer))

    def read_with_hook(self,hook,prompt=None,termitor=ac.ks_finish):
        self.hook = hook
        self.frame.write(ac.save + ac.move2(self.start_line,0) + ac.kill_line)
        if prompt :
            self.frame.write(prompt)
        elif hasattr(self,'prompt') :
            self.frame.write(self.prompt)
        self.reset(refresh=False)
        while True :
            data = self.frame.read_secret()
            if data in termitor :
                break
            self.send_with_hook(data)
        self.frame.write(ac.move2(self.start_line,0) +
                         ac.kill_line + self.text + ac.restore)
        return self.fetch()

    def hidden(self):
        self.frame.write(ac.move2(self.start_line,0) + self.text)

class UnicodeTextInput(BaseInput):

    def send(self,u_data):
        if u_data in self.key_maps :
            getattr(self,self.key_maps[u_data])()
        try:
            if len(self.buffer) + len(u_data) < self.buffer_size \
                    and self.acceptable(u_data) :
                self.push(u_data)
        except UnicodeDecodeError:
            pass
        
    def push(self,u_data):
        super(UnicodeTextInput,self).push(list(u_data))
        self.frame.write(u_data)
        
    def delete(self):
        raise NotImplementedError

    def acceptable(self,u_data):
        raise NotImplementedError

class zhTextInput(UnicodeTextInput):

    def acceptable(self,u_data):
        return (u_data in ac.printable ) or ac.is_chchar(u_data)

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

    def init(self):
        super(DatePicker,self).init(8)

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

    def fetch_str(self):
        text = self.buffer[:]
        text[6:6]='-'
        text[4:4]='-'
        return ''.join(text)

    def send(self,data):
        super(DatePicker,self).send(data)
        print self.buffer
        l = len(self.buffer)
        if l == 4 or l == 6 :
            self.frame.write('-')

    def delete(self):
        l = len(self.buffer)
        if l == 4 or l == 6 :
            self.frame.write(ac.backspace)
        super(DatePicker,self).delete()

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
