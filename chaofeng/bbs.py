__metaclass__ = type

import eventlet
from chaofeng import ascii
from chaofeng.g import static,mark
# from eventlet.green.socket import getnameinfo,AI_NUMERICHOST
import traceback

class GotoInterrupt(Exception):
    
    def __init__(self,to_where,args,kwargs):
        self.to_where = to_where
        self.args = args
        self.kwargs = kwargs

class EndInterrupt(Exception): pass

class FrameInterrupt(Exception):

    def __init__(self,callback_name):
        self.callback_name = callback_name

class Session:

    def __init__(self):
        self._dict = {}
        
    def __getitem__(self,name):
        return self._dict.get(name)

    def __setitem__(self,name,value):
        self._dict[name] = value
        
class Frame:

    def __init__(self,server,sock,session):
        self.session = session
        self.server = server
        self.sock = sock
        self._subframe = []
        self._loading = []

    def sub(self,subframe,*args,**kwargs):
        t = subframe(self.server,self.sock,self.session)
        t.initialize(*args,**kwargs)
        t._father = self
        self._subframe.append(t)
        return t

    def load(self,uix,*args,**kwargs):
        t = uix.new(self)
        t.init(*args,**kwargs)
        self._loading.append(t)
        return t
    
    def get(self,data):
        pass

    def initialize(self):
        pass

    def refresh(self):
        pass

    def clear(self):
        pass

    def fetch(self):
        pass

    def loop(self):
        while True :
            self.read()

    def read_until(self,termitor=['\r','\n','\r\x00']):
        while True :
            data = self.sock.recv(1024)
            if not data : self.close()
            elif data in termitor :
                return self.fetch()
            else:
                self.get(data)
                self._father.get(data)

    def read(self,buffer_size=1024):
        data = self.sock.recv(buffer_size)
        if not data :
            self.close()
        else:
            if self.get : self.get(data)
            return data

    def read_secret(self,buffer_size=1024):
        data = self.sock.recv(buffer_size)
        if not data :
            self.close()
        else:
            return data
        
    def pause(self):
        self.read_secret()
        
    def write(self,data):
        try:
            self.sock.send(data.encode('gbk'))
        except Exception,e:
            print e
            self.close()
            
    def raw_goto(self,where,*args,**kwargs):
        for s in self._subframe : s.clear()
        for u in self._loading : u.clear()
        self.clear()
        raise GotoInterrupt(where,args,kwargs)

    def goto(self,where_mark,*args,**kwargs):
        self.raw_goto(mark[where_mark],*args,**kwargs)

    def close(self):
        for s in self._subframe : s.clear()
        for u in self._loading : u.clear()
        self.clear()
        raise EndInterrupt

    def u(self,data):
        return unicode(data) if isinstance(data,str) else data

    def s(self,data):
        return str(data) if isinstance(data,unicode) else data

    def fm(self,format_str,d_tuple):
        return format_str % d_tuple

class BindFrame(Frame):

    def get(self,data):
        super(BindFrame,self).get(data)
        action = self.shortcuts.get(data)
        if action and hasattr(self,'do_'+action) :
            getattr(self,'do_'+action)()

class Server:

    def __init__(self,root,host='0.0.0.0',port=5000,max_connect=5000):
        self.sock  = eventlet.listen((host,port))
        self._pool = eventlet.GreenPool(max_connect)
        self.root  = root
        self.max_connect = max_connect
        self.sessions = []
        
    def run(self,load_static=False):

        root = self.root
        if load_static :
            static.load()
        
        def new_connect(sock,addr):
            next_frame = root
            session = Session()
            session.ip,session.port = sock.getpeername()
            session.shortcuts = {}
            sock.send(ascii.CMD_CHAR_PER)
            flag = True
            args = []
            kwargs = {}
            while flag:
                try:
                    now = next_frame(self,sock,session)
                    now.initialize(*args,**kwargs)
                    now.loop()
                    flag = False
                except GotoInterrupt as e:
                    next_frame = e.to_where
                    args = e.args
                    kwargs = e.kwargs
                except EndInterrupt:
                    break
                except FrameInterrupt,e:
                    e.callback()
                except Exception,e :
                    traceback.print_exc()
                    next_frame = mark['bad_ending']
                    args = [e]
                    kwargs = {}
                
        s = self.sock
        try:
            eventlet.serve(s,new_connect)
        except KeyboardInterrupt:
            pass
