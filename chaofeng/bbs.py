# -*- coding: utf-8 -*-

'''
    chaofeng.bbs
    ~~~~~~~~~~~~

    This module implements the core of chaofeng.
'''

__metaclass__ = type

import eventlet
from eventlet.green import socket
from eventlet import tpool
from eventlet.timeout import Timeout 
from chaofeng import ascii
from chaofeng.g import mark
import functools 
# from eventlet.green.socket import getnameinfo,AI_NUMERICHOST
import traceback
import datetime
import sys

class FatalException(Exception):
    '''
    A base class for finish a session.
    '''
    pass

class BrokenConnection(FatalException):
    '''
    This exception will be raise while the remote connection is
    close.

    The ``id`` and ``port`` attribultes is the ip/port of the
    remote connection,
    '''
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

class TravelInterrupt(Exception):
    '''
    A base class for travel across the frame.
    '''
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

    def __str__(self):
        return '[RUNNER] goto /%s/ (%s) (%s)' % (self.to_where, self.args, self.kwargs)

class WakeupInterrupt(TravelInterrupt):

    def __init__(self,frame):
        self.f = frame

    def build(self, server, sock, session):
        return self.f

    def work(self, f):
        f.restore()

class SafeInterrupt(Exception):
    pass

class EndInterrupt(Exception):
    pass

class BadEndInterrupt(Exception):
    pass

class Session:

    '''A dict-like object with charset attribute.'''

    def __init__(self, codecs='gbk'):
        self._dict = {}
        self.set_charset(codecs)
        
    def __getitem__(self,name):
        ''' S[name] --> Dict.get(name) '''
        return self._dict.get(name)

    def __setitem__(self,name,value):
        ''' Like dict[name] = value. '''
        self._dict[name] = value

    def pop(self, name, argv=None):
        return self._dict.pop(name, argv)

    def set_charset(self,codecs):
        ''' Set the charset attribute. '''
        self.charset = codecs

class Frame:

    '''Subclass this class and define initialize() to make a frame.

    Each session holds one and only one frame.
    '''

    WRITE_BUFFER_SIZE = 4096
                
    def _socket_holder(self, buffer_size=1024):
        while True:
            data = self.sock.recv(buffer_size)
            # print repr(data)
            if len(data) == 1 and ascii.is_gbk_zh(data):  # Ugly
                data += self.sock.recv(1)
            if data in ascii.CC:
                # print ascii.CC[data]
                yield ascii.CC[data]
            elif data:
                try:
                    data = self.u(data)
                except UnicodeDecodeError:
                    print 'UnicodeDecodeError'
                    continue
                for char in data:
                    yield char
            else:
                raise BrokenConnection(self.session.ip, self.session.port)
    
    def __init__(self, server, sock, session):
        self.session = session
        self.server = server
        self.sock = sock
        self.stream = self._socket_holder()
        self._subframe = []
        self._loading = []
        self._buffer = []

    def read_secret(self):
        '''Get an char/char sequence from the remote client.
        Basic useage:

            if self.read_secret == 'a' :
                do_something_while_a_press()
        
        '''
        if self._buffer:
            self.fflush()
        char = self.stream.next()
        if char == ascii.esc:
            buf = [char]
            tree = ascii.ascii_tree[char]
            while True:
                tchar = self.stream.next()
                buf.append(tchar)
                if tchar in tree:
                    tree = tree[tchar]
                    if not tree:
                        return u''.join(buf)
                else:
                    return u''.join(buf)
        if char == u'\x1b\0':
            return u'\x1b'
        return char

    def read(self):
        '''Get an char/char sequence from the remote client.
        Call self.get(char) and return char
        '''
        char = self.read_secret()
        if self.get :
            self.get(char)
        return char

    def pause(self,prompt=None):
        '''Wait any character to continue.

        :param prompt:  the prompt for this pause
        '''
        if prompt is not None:
            self.write(prompt)
        self.read_secret()

    # def write_raw(self,data):
    #     # if IAC in data:
    #         # data = data.replace(IAC, IAC+IAC)
    #     self.sock.send(data)
        
    def push(self, data):
        try:
            data = self.s(data)
        except IOError, e:
            traceback.print_exc()
            self.close()
        except Exception,e:
            print (self, e)
            traceback.print_exc()
            print repr(data)
            self.close()
        except:
            traceback.print_exc()
            raise e
        else:
            self._buffer.append(data)
        if len(data) > self.WRITE_BUFFER_SIZE :
            self.fflush()

    def fflush(self):
        try:
            self.sock.send(''.join(self._buffer))
        except socket.error as e:
            # print (self, e)
            # traceback.print_exc()
            self.close()
        self._buffer = []

    def write(self,data):
        self.push(data)
        self.fflush()

    def writeln(self,data=''):
        self.push(data)
        self.push('\r\n')
        self.fflush()

    def load(self, uimod, *args, **kwargs):
        '''Load an UI module. Return the uimod.'''
        m = uimod(self)
        m.init(*args,**kwargs)
        self._loading.append(m)
        return m
    
    def get(self,data):
        '''Hook for get a input.'''
        pass

    def initialize(self):
        '''Hook for subclass initialization.'''
        pass

    def clear(self):
        '''Hook at the end of current frame. These functions are
        executed when this frame is finish, even if some exception
        raise or the remote is close.
        '''
        pass

    def leave(self):
        pass

    def interrupt(self, e):
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

    def _clear(self):
        for s in self._subframe : s.clear()
        for u in self._loading : u.clear()
            
    def raw_goto(self,where,*args,**kwargs):
        self._clear()
        self.clear()
        self.leave()
        raise GotoInterrupt(where,args,kwargs)

    def goto(self,where_mark,*args,**kwargs):
        self.raw_goto(mark[where_mark],*args,**kwargs)

    def wakeup(self,frame):
        self._clear()
        self.clear()
        self.leave()
        raise WakeupInterrupt(frame)

    def close(self):
        for s in self._subframe : s.clear()
        for u in self._loading : u.clear()
        self.leave()
        raise EndInterrupt

    def u(self,s):
        return unicode(s, encoding=self.session.charset, errors='replace')

    def s(self,u):
        return u.encode(self.session.charset, errors='replace')

@mark('finish')
class FinishFrame(Frame):
    
    def finish(self,e):
        pass
    def bad_ending(self,e):
        pass    

class Server:

    def __init__(self,root,host='0.0.0.0', sessioncls=Session, port=5000,max_connect=5000):
        self.sock  = eventlet.listen((host,port))
        self.root  = root
        self.max_connect = max_connect
        self.sessions = []
        self.sessioncls = sessioncls
        
    def run(self):

        root = self.root

        def new_connect(sock,addr):
            session = self.sessioncls()
            session.ip,session.port = sock.getpeername()
            session.shortcuts = {}

            sock.send(ascii.CMD_CHAR_PER)
            r = sock.recv(1024)

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
                    except SafeInterrupt as e:
                        now.interrupt(e)
                    else:
                        raise EndInterrupt
            except EndInterrupt as e:
                now.clear()
                t = mark['finish'](self,sock,session)
                t.finish(e)
            except Exception,e :
                print 'Bad Ending [%s]' % session.ip
                print 'runner: %s ' % runner
                traceback.print_exc()
                try: now.clear()
                except: traceback.print_exc()
                try:
                    t = mark['finish'](self,sock,session)
                    t.bad_ending(e)
                except :
                    traceback.print_exc()
            except : pass
            print 'End [%s]' % session.ip
            sock.close()
                
        s = self.sock
        while True:
            try:
                print 'RUNNING -- %s' % datetime.datetime.now().ctime()
                eventlet.serve(s,new_connect,concurrency=self.max_connect)
            except KeyboardInterrupt:
                break
            except Exception:
                pass
            except :
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

class AsyncTimeLimitError(Exception):
    pass

def asynchronous(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        with Timeout( 10, AsyncTimeLimitError):
            return tpool.execute(f, *args, **kwargs)
    return wrapper

# def asynchronous_t(max_delay):
#     def _(f):
#         @functools.wraps(f)
#         def wrapper(*args,**kwargs):
#             print 2
#             with Timeout( max_delay, AsyncTimeLimitError):
#                 return tpool.execute(f, *args, **kwargs)
#         return wrapper
#     return _

# def asynchronous_n(max_retry):
#     def _(f):
#         @functools.wraps(f)
#         def wrapper(*args,**kwargs):
#             for i in range(max_retry):
#                 try:
#                     return f(*args,**kwargs)
#                 except AsyncTimeLimitError:
#                     pass
#             else:
#                 raise AsyncTimeLimitError
#         return wrapper
#     return _

class PluginHolder:

    def __init__(self, hookname=None):
        if hookname :
            self._hook = dict( (name, []) for name in hookname)
        else:
            self._hook = []
        self._action = {}
        
    def add_action(self, name):
        def mark_inner(f):
            self._action[name] = f
            return f
        return mark_inner

    def do_action_ifex(self, name, frame):
        if name in self._action:
            self._action[name](frame)

    def hook_up(self, hookname):
        def mark_inner(f):
            try:
                self._hook[hookname].append(f)
            except KeyError:
                raise ValueError(u'No such hook `%s` ' % hookname)
            return f
        return mark_inner

    def get_all_hook(self, hookname):
        try:
            return self._hook[hookname]
        except KeyError:
            raise ValueError(u'No such hook `%s`' % hookname)
