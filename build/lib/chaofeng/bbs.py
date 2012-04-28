__metaclass__ = type

import eventlet
from chaofeng import ascii
from chaofeng.g import static
# from eventlet.green.socket import getnameinfo,AI_NUMERICHOST

class GotoInterrupt(Exception):
    
    def __init__(self,to_where,kwargs):
        self.to_where = to_where
        self.kwargs = kwargs

class EndInterrupt(Exception): pass

class Frame:

    buffer_size = 1024
    
    g = {}

    def __init__(self,server,sock,session):
        self.session = session
        self.server = server
        self.sock = sock

    def loop(self):
        while True :
            self.read()

    def initialize(self):
        pass

    def clear(self):
        pass

    get = None

    def read(self,buffer_size=1024):
        data = self.sock.recv(buffer_size)
        if not data :
            self.close()
        else:
            if self.get : self.get(data)
            return data
            
    def write(self,data):
        self.sock.send(data.encode('gbk'))

    def goto(self,where,**kwargs):
        raise GotoInterrupt(where,kwargs)

    def close(self):
        self.clear()
        raise EndInterrupt

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
            session = {}
            session['ip'],session['port'] = sock.getpeername()
            sock.send(ascii.CMD_CHAR_PER)
            flag = True
            kwargs = {}
            while flag:
                try:
                    now = next_frame(self,sock,session)
                    now.initialize(**kwargs)
                    now.loop()
                    flag = False
                except GotoInterrupt as e:
                    next_frame = e.to_where
                    kwargs = e.kwargs
                except EndInterrupt:
                    break
                
        s = self.sock
        try:
            eventlet.serve(s,new_connect)
        except KeyboardInterrupt:
            pass
