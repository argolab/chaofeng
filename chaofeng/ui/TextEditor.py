from baseui import BaseUI
import chaofeng.ascii as ac
from copy import deepcopy

class TextBufferMeta(type):

    def __new__(cls,names,bases,attrs):
        cls = super(TextBufferMeta,cls).__new__(names,bases,attrs)
        if hasattr(cls,'__textmodule__'):
            if names not in cls.__textmodule__ :
                cls.__clsinit__()
                cls.__textmodule__.add(names)
        else:
            cls.__textmodule__ = frozenset(names)

    def __clsinit__(cls):
        pass

class TextBuffer(BaseUI):

    _hooks = {}

    def __init__(self,height=23):
        self.h = height  # the number of the screen height
                         # notice that last line use to be bottom bar

    def init(self,**kwargs):
        self.kwargs = kwargs
        self.do_command('init_iter')

    def init_iter(self):
        pass

    def _action_hook(self,cmd):
        for action in self.hooks :
            getattr(self,action)()

    @classmethod
    def add_hook(cls,cmdname,action):
        if hasattr(cls,'%s_iter'% cmdname):
            if cmdname is cls._hooks :
                cls._hooks[cmdname].append(action)
            else:
                cls._hooks[cmdname]=[action]
        else:
            raise ValueError,"No such command. [%s]" % cmdname

            for action in self.hooks :
                action(self)

    def do_command(self,cmd):
        do_iter = '%s_iter' % cmd
        if hasattr(self,do_iter):
            getattr(self,do_iter)()
            self.bottom_bar()
            if cmd in self.save_step_cmd:
                self.save_cmd_step_iter()
            if cmd in self.save_force_cmd:
                self.save_history_iter()
        else:
            raise ValueError,"No such command. [%s]" % do_iter

    def bottom_bar(self):
        self.write((ac.move2(self.h+1, 0) + 
                   ac.kill_line + '%s(%d,%d){%d,%d}[%s,%s)' % (self.getline(),
                                                               self.l,self.r,
                                                               self.ml,self.mr,
                                                               self.s, self.s+self.h))[:80])
        self._fix_cursor()
        
    def init(self):
        self.buf=[[]]
        self.l = 0    # current line number
        self.r = 0    # current row number
        self.s = 0    # first visible line number

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
            self._fix_cursor()

    def insert_lines(self,buf):
        self.buf[self.l:self.l] = buf
        buf.reverse()
        self.write(('\r'+ac.insert1))
        self.write(('\r'+ac.insert1).join(map(lambda x: ''.join(x),
                                              buf)))
        self._fix_cursor()

    def total_line(self):
        return len(self.buf)

    def new_line_next(self):
        self.l += 1
        self.r = 0
        self.write('\r\n'+ac.insert1)
        self.buf[self.l:self.l]=[[]]
        if self.l >= self.s + self.h:
            print 'new'
            self.set_start(self.l - self.h + 1)

    def write(self,data):
        self.frame.write(data)

    def refresh_all(self):
        self.write(ac.clear+ac.move0)
        self.write(self.getscreen())

    def set_start(self,start):
        print '%s [%s,%s)' % (self.l,start,start + self.h)
        if (start > self.l) or (self.l >= start + self.h):
            raise ValueError,"Make sure that s <= self.l < s+h"
        if start == self.s:
            return
        print ('*',start,self.s,self.l)
        if (self.s > start) and (self.s <= start + 10):
            offset = self.s - start
            self.write(ac.move0 + ac.insertn(offset) + '\r')
            self.write('\r\n'.join(self.getlines(start,self.s)))
            self.s = start
            self._fix_cursor()
        elif (start > self.s) and (start <= self.s + 10):
            astart = self.s + self.h # Append Start
            self.write(ac.move2(self.h+1,0))
            self.write(ac.kill_line)
            self.write('\r\n'.join(self.getlines(astart, start + self.h)))
            self.write('\r\n')
            self.s = start
            self._fix_cursor()
        else :
            self.s = start
            self.refresh_all()

    def earse_to_end(self):
        del self.buf[self.l][self.r:]
        self.write(ac.kill_to_end)

    def visible_width(self):
        return reduce(lambda acc,obj: acc+self.char_width(obj),
                      self.buf[self.l][:self.r],1)

    def _fix_cursor(self):
        self.r = min(self.r, self.getlen())
        cr = self.visible_width()
        self.write(ac.move2(self.l-self.s+1, cr))

    def replace_charlist(self,charlist):
        self.buf[self.l][self.r:] = charlist
        self.r += len(charlist)
        charlist[0:0] = [ac.kill_line]
        self.display(''.join(charlist))  #!!!!!!!!!!!!!!!!!

    def move_up(self,offset=1):
        if offset == 0:
            return
        if self.l >= offset :
            self.l -= offset
        else:
            self.l = 0
        if self.l <= self.s :
            self.set_start(self.l)
        self._fix_cursor()
            
    def move_down(self,offset=1):
        if offset == 0:
            return
        length = self.total_line()
        if self.l + offset < length :
            self.l += offset
        else:
            self.l = length - 1
        print ('down', self.s, self.s+self.h, self.l+1)
        if self.l >= self.s + self.h :
            self.set_start(self.l - self.h + 1)
        self._fix_cursor()

    def goto_pos(self,nl,nr):
        self.l = max(0,min(nl,self.total_line()-1))
        self.r = max(0,min(nr,self.getlen()-1))
        if self.l<self.s :
            self.set_start(self.l)
        elif self.l>=self.s+self.h :
            self.set_start(max(0,self.l-self.h))
        self._fix_cursor()
        
    def move_right(self,offset=1):
        if offset == 0 :
            return
        if self.r + offset <= self.getlen():
            self.r += offset
            self._fix_cursor()

    def char_width(self,char):
        if char in ac.printable :
            return 1
        if ac.is_chchar(char):
            return 2
        return len(char)
    
    def move_left(self,offset=1):
        if offset == 0 :
            return
        if self.r >= offset :
            self.r -= offset
            self._fix_cursor()

    def move_line_beginning(self):
        self.r = 0
        self.write(ac.line_beginning)

    def move_line_end(self)
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

class TextEditor_Cursor(TextBuffer):
        
    def move_left_iter(self):
        l,r = self.getlr()
        if r == 0 :
            self.move_up()
            self.move_line_end_iter()
        else:
            self.move_left()

    def move_right_iter(self):
        l,r = self.getlr()
        length = self.getlen()
        if r == length :
            self.move_down()
            self.move_line_beginning()
        else:
            self.move_right()

    def move_up_iter(self,offset=1):
        self.move_up(offset=offset)

    def move_down_iter(self,offset=1):
        self.move_down(offset=1)

    def move_line_end_iter(self):
        self.move_line_end()
        
    def move_line_beginning_iter(self):
        self.move_line_beginning()

    def move_firstline_iter(self):
        self.goto_pos(0,0)

    def move_lastline_iter(self):
        self.goto_pos(0,0)

    def page_down_iter(self):
        self.move_down(self.h)

    def page_up_iter(self):
        self.move_up(self.h)

class TextEditor_Edit(TextBuffer):

    def insert_iter(self,char):
        d = self.getline_cursor()
        l = len(d)
        d.insert(0,char)
        self.replace_charlist(d)
        self.move_left(l)

    def safe_insert_iter(self,char):
        for c in self.frame.u(''.join(char)):
            if c in ac.printable or ac.is_chchar(c):
                self.insert_iter(c)

    def insert_line_iter(self,charlist):
        self.replace_charlist(charlist)
        self.new_line_next()

    def new_line_iter(self):
        d = self.getline_cursor()
        self.earse_to_end()
        self.new_line_next()
        self.replace_charlist(d)
        self.move_line_beginning()

    def kill_whole_line_iter(self):
        self.remove_lines()

    def kill_to_end_iter(self):
        d = self.getline_cursor()
        if d :
            self.earse_to_end()
        else:
            self.remove_lines()

    def backspace_iter(self):
        if self.r <= 0 :
            if self.l <= 0 :
                return
            d = self.getline()
            self.remove_lines()
            self.move_up()
            self.move_line_end()
            self.replace_charlist(d)
            self.move_left(len(d)-1)
        else:
            self.move_left()
            d = self.getline_cursor()
            del d[0]
            self.replace_charlist(d)
            self.move_left(len(d)-1)

    def delete_iter(self):
        if self.r >= self.getlen():
            l,r = self.getlr()
            self.goto_pos(self.l+1,0)
            d = self.getline()
            self.remove_lines()
            self.goto_pos(l,r)
            self.replace_charlist(d)
            self.move_left(len(d)-1)
        else:
            d = self.getline_cursor()
            del d[0]
            self.replace_charlist(d)
            self.move_left(len(d)-1)

class TextEditor_Mark(TextBuffer):

    def set_mark_iter(self):
        self.ml, self.mr = self.getlr()

    def get_mark(self):
        return self.ml, self.mr

    def exchange_pos_iter(self):
        tl,tr = self.get_mark()
        self.set_mark_iter()
        self.goto_pos(tl,tr)

    def get_pair(self):
        if (self.ml < self.l) or ((self.ml == self.l) and (self.mr < self.r)):
            return self.ml, self.mr, self.l,  self.r
        else:
            return self.l,  self.r,  self.ml, self.mr

    def remove_area_iter(self):
        minl,minr,maxl,maxr = self.get_pair()
        self.clipboard = self.getselect(minl,minr,maxl,maxr-1)
        self.goto_pos(maxl,maxr)  # first goto max, or it will be delete
        d = self.getline_cursor()
        self.goto_pos(minl+1,0)
        self.remove_lines(maxl-minl)
        self.goto_pos(minl,minr)
        self.replace_charlist(d)
        self.goto_pos(minl,minr)

    def paste_area_iter(self):
        self.new_line_next()
        self.insert_lines(self.clipboard)

class TextEditor_History(TextBuffer):

    save_step_cmd = set(("kill_whole_line","kill_to_end","delete_iter",
                         "insert","new_line","backspace","delete"))

    save_force_cmd = set()

    @classmethod
    def __clsinit__(cls):
        for cmd in cls.save_step_cmd:
            cls.add_hook(cmd,"save_cmd_step_iter")
        for cmd in cls.save_force_cmd:
            cls.add_hook(cmd,"save_history_iter")

    def save_cmd_step_iter(self):
        self._dd += 1
        if self._dd >= self._dis:
            self.save_history_iter()        

    def insert_with_history_iter(self,char):
        self.insert_iter(self,char)
        self.save_cmd_step_iter()  #!!!!!!!!!!!!!!!!!

    def save_history_iter(self):
        self._dd = 0
        self._top += 1
        if self._top == self._hislen:
            self._top = 0
        self.history[self._top] = self.status()
        self.message('Snapshot! [%s' % self._top)

    def restore_history_iter(self):
        self.restore(self.history[self._top])
        self.message('Restore! [%s' % self._top)
        self._top -= 1
        if self._top < 0 :
            self._top = self._hislen - 1

class TextEditor(TextBuffer):

    def __init__(self,height=23,dis=5,hislen=10):
        super(TextEditor,self).__init__(height)
        self.history = [[],]*10
        self._hislen = hislen
        self._dis = dis
        self._top = 0
        self._dd = 0
        self.set_mark_iter()
        self.clipboard =[[]]

    def refresh_iter(self):
        self.refresh_all()

    def message(self,msg):
        print msg

    def do_command(self,cmd):
        do_iter = '%s_iter' % cmd
        if hasattr(self,do_iter):
            getattr(self,do_iter)()
            self.bottom_bar()
            if cmd in self.save_step_cmd:
                self.save_cmd_step_iter()
            if cmd in self.save_force_cmd:
                self.save_history_iter()
        else:
            raise ValueError,"No such command. [%s]" % do_iter
