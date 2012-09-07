__metaclass__ = type

from copy import copy

class BaseUI:

    is_destory_screen = True

    def __init__(self, frame):
        self.frame = frame
        
    def init(self):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def clear(self):
        pass

    def do_command(self, action):
        if action:
            getattr(self, action)()
            self.frame.fflush()

    def readline(self, buf_size=20):
        u'''
        Read one line.
        '''
        buf = []
        while True :
            ds = self.frame.read_secret()
            for d in ds :
                if d == '\x7f' :
                    if buf:
                        buf.pop()
                        self.write(ac.backspace)
                        continue
                elif d == '\n' :
                    return u''.join(buf)
                elif d == ac.k_ctrl_c:
                    return False
                elif (len(buf) < buf_size) and d.isalnum():
                    buf.append(d)
                    self.write(d)
        return u''.join(buf)                        
