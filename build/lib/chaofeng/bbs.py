__metaclass__ = type

import eventlet
from eventlet.green import socket
from eventlet import tpool
from eventlet.timeout import Timeout 
from chaofeng import ascii
from chaofeng.g import static,mark
import functools 
# from eventlet.green.socket import getnameinfo,AI_NUMERICHOST
import traceback
import sys

class TravelInterrupt(Exception):
    pass

class GotoInterrupt(TravelInterrupt):
    
    def __init__(self,to_where,args,kwargs):
        self.to_where = to_where
        self.args = args
        self.kwargs = kwargs

    def build(self, server, sock, session):
        return self.to_where(server, sock, session)

    def work(self, f):
        f.initialize(*self.args, **self.kwargs)

class WakeupInterrupt(TravelInterrupt):

    def __init__(self,frame):
        self.f = frame

    def build(self, server, sock, session):
        return self.f

    def work(self, f):
        f.restore()

class EndInterrupt(Exception): pass

class BadEndInterrupt(Exception): pass



class Session:

    def __init__(self,codecs='gbk'):
        self._dict = {}
        self.set_charset(codecs)
        
    def __getitem__(self,name):
        return self._dict.get(name)

    def __setitem__(self,name,value):
        self._dict[name] = value

    def set_charset(self,codecs):
        self.charset = codecs

class FrameMeta(type):

    def __new__(cls,name,bases,attrs):
        res = super(FrameMeta,cls).__new__(cls,name,bases,attrs)
        res.__clsinit__()
        return res

    def __clsinit__(cls):
        pass

class Frame:

    __metaclass__ = FrameMeta

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

    def run(self):
        pass

    def loop(self):
        while True :
            self.read()

    def msg(self,msg,*args):
        if self.debuglevel > 0:
            print 'CONN(%s, %s):' % (self.session,ip, self.session.port)
            if args :
                print msg % args
            else:
                print msg

    def read(self,buffer_size=1024):
        data = self.sock.recv(buffer_size)
        if not data :
            raise BadEndInterrupt
        else:
            if self.get : self.get(data)
            try:
                data = self.u(data)
            except: pass
            return data

    def read_secret(self,buffer_size=1024):
        data = self.sock.recv(buffer_size)
        if not data :
            raise BadEndInterrupt
        else:
            return data
        
    def pause(self,prompt=None):
        if prompt is not None:
            self.write(prompt)
        self.read_secret()

    def write_raw(self,data):
        # if IAC in data:
            # data = data.replace(IAC, IAC+IAC)
        self.sock.send(data)
        
    def write(self,data):
        # if IAC in data:
            # data = data.replace(IAC, IAC+IAC)
        try:
            self.sock.send(self.s(data))
        except Exception,e:
            print e
            traceback.print_exc()
            self.close()

    def writeln(self,data=''):
        self.write(data + '\r\n')

    def _clear(self):
        for s in self._subframe : s.clear()
        for u in self._loading : u.clear()
            
    def raw_goto(self,where,*args,**kwargs):
        self._clear()
        self.clear()
        raise GotoInterrupt(where,args,kwargs)

    def goto(self,where_mark,*args,**kwargs):
        self.raw_goto(mark[where_mark],*args,**kwargs)

    def wakeup(self,frame):
        self._clear()
        self.clear()
        raise WakeupInterrupt(frame)

    def close(self):
        for s in self._subframe : s.clear()
        for u in self._loading : u.clear()
        self.clear()
        raise EndInterrupt

    @property
    def charset(self):
        return 'gbk'

    def u(self,s):
        return s.decode(self.charset)

    def s(self,u):
        return u.encode(self.charset)

    def fm(self,format_str,d_tuple):
        return format_str % d_tuple

class Server:

    def __init__(self,root,host='0.0.0.0',port=5000,max_connect=5000):
        self.sock  = eventlet.listen((host,port))
        self.root  = root
        self.max_connect = max_connect
        self.sessions = []
        
    def run(self):

        root = self.root
        finish_frame = mark['finish']

        def new_connect(sock,addr):
            session = Session()
            session.ip,session.port = sock.getpeername()
            session.shortcuts = {}
            sock.send(ascii.CMD_CHAR_PER)

            runner = GotoInterrupt(root,(),{})
            
            try:
                while True:
                    try:
                        now = runner.build(self, sock, session)
                        runner.work(now)
                        now.loop()
                    except TravelInterrupt as e:
                        now.clear()
                        runner = e
                    else:
                        raise EndInterrupt
            except EndInterrupt,e:
                now.clear()
                t = finish_frame(self,sock,session)
                t.finish(e)
            except Exception,e :
                print 'Bad Ending [%s]' % session.ip
                traceback.print_exc()
                try: now.clear()
                except: traceback.print_exc()
                try:
                    t = finish_frame(self,sock,session)
                    t.bad_ending(e)
                except :
                    traceback.print_exc()
            except : pass
            print 'End [%s]' % session.ip
                
        s = self.sock
        try:
            eventlet.serve(s,new_connect,concurrency=self.max_connect)
        except KeyboardInterrupt:
            pass

# def asynchronous(f):
#     @functools.wraps(f)
#     def wrapper(*args,**kwargs):
#         e = eventlet.event.Event()
#         def inner_exec():
#             res = f(*args,**kwargs)
#             e.send(res)
#         res = e.wait()
#         return res
#     return wrapper

class AsyncTimeLimitError(Exception):pass

def asynchronous(f):
    return asynchronous_t(3)(f)

def asynchronous_t(max_delay):
    def _(f):
        @functools.wraps(f)
        def wrapper(*args,**kwargs):
            with Timeout( max_delay, AsyncTimeLimitError):
                return tpool.execute(f, *args, **kwargs)
        return wrapper
    return _

def asynchronous_n(max_retry):
    def _(f):
        @functools.wraps(f)
        def wrapper(*args,**kwargs):
            for i in range(max_retry):
                try:
                    return f(*args,**kwargs)
                except AsyncTimeLimitError:
                    pass
            else:
                raise AsyncTimeLimitError
        return wrapper
    return _
