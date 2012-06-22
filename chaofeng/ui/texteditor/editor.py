import chaofeng.ascii as ac
from copy import deepcopy

class TextEditorMeta(type):

    def __new__(cls,names,bases,attrs):
        cls = super(TextEditorMeta,cls).__new__(cls,names,bases,attrs)
        if not hasattr(cls,'__textmodule__'):
            cls.__textmodule__ = set()
        if names not in cls.__textmodule__ :
                cls.__textmodule__.add(cls)
        return cls

    def __modinit__(cls):
        pass

    def add_hook(cls,cmdname,action):
        if (cmdname in cls._hooks) or hasattr(cls,'%s_iter'% cmdname):
            if cmdname not in cls._hooks :
                cls._hooks[cmdname] = set()
            cls._hooks[cmdname].add(action)

class TextEditor_OX:

    __metaclass__ = TextEditorMeta
    _hooks = {
        "__init__": set(),
        "__aftercmd__" : set(),
        # "__beforecmd__" : frozenset(),
        }
        
    def action_hook(self,hookname):
        for action in self._hooks[hookname]:
            getattr(self,action)()

    def do_command(self,cmd):
        do_iter = '%s_iter' % cmd
        if hasattr(self,do_iter):
            getattr(self,do_iter)()
            self.action_hook("__aftercmd__")
            if self._hooks.get(cmd) and cmd in self._hooks[cmd] :
                self.action_hook(cmd)
        else:
            raise ValueError,"No such command. [%s]" % do_iter

class TextEditorModule(TextEditor_OX):
    pass

class TextBuffer(TextEditor_OX):

    @classmethod
    def __initmodules__(cls,**kwargs):
        cls.__metaclass__.kwargs = kwargs
        cls.h = kwargs['height']
        cls.add_hook("__aftercmd__","bottom_bar")
        cls.add_hook("__init__","init_buf")
        for mod in cls.__textmodule__ :
            mod.__modinit__()

    def init_buf(self,buf=None,r=0,l=0,s=0,**kwargs):
        self.kwargs = kwargs
        self.buf = buf or [[]]
        self.l = l    # current line number
        self.r = r    # current row number
        self.s = s    # first visible line number

    @property
    def status(self):
        return dict(buf=self.buf,
                    l=self.l, r=self.r, s=self.s)

    def bottom_bar(self):
        self.write((ac.move2(self.h+1, 0) + ac.kill_line +
                   '[%d,%d] %s' % (self.l,self.r, ''.join(self.getline())[:80])))
        self.fix_cursor()

    def write(self,char):
        print char
        
    def getlines(self,f,t):
        buf = map(lambda x: ''.join(x),
                   self.buf[f:t])
        l = len(self.buf)
        if t > l :
            buf.extend('~'*(t-l))
        return buf

    def getscreen(self):
        return '\r\n'.join(map(lambda x: ''.join(x),
                               self.getlines(self.s,self.s+self.h)))

    def getall(self):
        return '\r\n'.join(map(lambda x: ''.join(x),
                               self.buf))

    def getselect(self,minl,minr,maxl,maxr):
        total = self.total_line()
        minl = max(0,min(minl,self.total_line))
        maxl = max(0,min(maxl,self.total_line))
        if minl == maxl :
            return [self.buf[minl][minr:maxr+1]]
        else:
            return [self.buf[minl][minr:]] + self.buf[minl+1:maxl] + [self.buf[maxl][:maxr+1]]

    def new_line(self):
        self.buf[self.l:self.l]=[[]]
        self.r = 0
        self.write('\r' + ac.insert1)

    def remove_lines(self,num=1):
        if self.total_line():
            last = self.l + num
            self.move_line_beginning()
            self.write(ac.clear1)
            if last >= self.total_line():
                self.buf[self.l:]=[[]]
            else:
                del self.buf[self.l:last]
            self.write('\r\n'.join(self.getlines(self.l,self.s+self.h)))
            self.r = 0
            self.fix_cursor()

    def insert_lines(self,buf):
        self.buf[self.l:self.l] = buf
        buf.reverse()
        self.write(('\r'+ac.insert1))
        self.write(('\r'+ac.insert1).join(map(lambda x: ''.join(x),
                                              buf)))
        self.fix_cursor()

    def total_line(self):
        return len(self.buf)

    def new_line_next(self):
        self.l += 1
        self.r = 0
        self.write('\r\n'+ac.insert1)
        self.buf[self.l:self.l]=[[]]
        if self.l >= self.s + self.h:
            self.set_start(self.l - self.h + 1)

    def refresh_all(self):
        self.write(ac.clear+ac.move0)
        self.write(self.getscreen())

    def set_start(self,start):
        if (start > self.l) or (self.l >= start + self.h):
            raise ValueError,"Make sure that s <= self.l < s+h"
        if start == self.s:
            return
        if (self.s > start) and (self.s <= start + 10):
            offset = self.s - start
            self.write(ac.move0 + ac.insertn(offset) + '\r')
            self.write('\r\n'.join(self.getlines(start,self.s)))
            self.s = start
            self.fix_cursor()
        elif (start > self.s) and (start <= self.s + 10):
            astart = self.s + self.h # Append Start
            self.write(ac.move2(self.h+1,0))
            self.write(ac.kill_line)
            self.write('\r\n'.join(self.getlines(astart, start + self.h)))
            self.write('\r\n')
            self.s = start
            self.fix_cursor()
        else :
            self.s = start
            self.refresh_all()

    def earse_to_end(self):
        del self.buf[self.l][self.r:]
        self.write(ac.kill_to_end)

    def visible_width(self):
        return reduce(lambda acc,obj: acc+self.char_width(obj),
                      self.buf[self.l][:self.r],1)

    def fix_cursor(self):
        self.r = min(self.r, self.getlen())
        cr = self.visible_width()
        self.write(ac.move2(self.l-self.s+1, cr))

    def replace_charlist(self,charlist):
        self.buf[self.l][self.r:] = charlist
        self.r += len(charlist)
        charlist[0:0] = [ac.kill_line]
        # self.display(''.join(charlist))  #!!!!!!!!!!!!!!!!!
        self.write(''.join(charlist))

    def move_up(self,offset=1):
        if offset == 0:
            return
        if self.l >= offset :
            self.l -= offset
        else:
            self.l = 0
        if self.l <= self.s :
            self.set_start(self.l)
        self.fix_cursor()
            
    def move_down(self,offset=1):
        if offset == 0:
            return
        length = self.total_line()
        if self.l + offset < length :
            self.l += offset
        else:
            self.l = length - 1
        if self.l >= self.s + self.h :
            self.set_start(self.l - self.h + 1)
        self.fix_cursor()

    def goto_pos(self,nl,nr):
        self.l = max(0,min(nl,self.total_line()-1))
        self.r = max(0,min(nr,self.getlen()-1))
        if self.l<self.s :
            self.set_start(self.l)
        elif self.l>=self.s+self.h :
            self.set_start(max(0,self.l-self.h))
        self.fix_cursor()
        
    def move_right(self,offset=1):
        if offset == 0 :
            return
        if self.r + offset <= self.getlen():
            self.r += offset
            self.fix_cursor()

    def char_width(self,char):
        return len(char)
    
    def move_left(self,offset=1):
        if offset == 0 :
            return
        if self.r >= offset :
            self.r -= offset
            self.fix_cursor()

    def move_line_beginning(self):
        self.r = 0
        self.write(ac.line_beginning)

    def move_line_end(self):
        length = self.getlen()
        self.move_right(length-self.r)
        
    def getlen(self):
        return len(self.buf[self.l])

    def getlr(self):
        return self.l, self.r

    def getline(self):
        return self.buf[self.l]

    def getline_cursor(self):
        return self.buf[self.l][self.r:]

    def replace(self,char):
        self.buf[self.l][self.r] = char
        self.write(char)

    def status(self):
        return (self.l,self.r,deepcopy(self.buf))

    def restore(self,s):
        if s:
            self.l,self.r,self.buf = s
            self.refresh_all()
