from baseui import BaseUI
import chaofeng.ascii as ac

class TextBuffer(BaseUI):

    key_maps = {}

    def __init__(self,height=24):
        self.h = height  # the number of the screen height
                         # notice that last line use to be bottom bar

    def _move_to(self,l,r):
        # if l > self.h or l < 0 or self.r <0 or self.r > self.getlen():
            # raise
        print (l,r)
        self.write(ac.move2(l+1,r+1))

    def bottom_bar(self):
        self.write(ac.move2(self.h, 0) + 
                   ac.kill_line + '%s(%d,%d)' % (self.getline(),self.l,self.r))
        self._move_to(self.l-self.s, self.r)

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
                               self.getlines(self.l,self.l+self.h)))

    def new_line(self):
        self.buf[self.l:self.l]=[[]]
        self.r = 0
        self.write('\r' + ac.insert1)
        
    def remove_whole_line(self):
        if self.l:
            del self.buf[self.l]
            self.move_line_beginning()
            self.write(ac.clear1)
            self.write('\r\n'.join(self.getlines(self.l,self.s+self.h)))

    def total_line(self):
        return len(self.buf)

    def new_line_next(self):
        self.l += 1
        self.r = 0
        self.write('\r\n'+ac.insert1)
        self.buf[self.l:self.l]=[[]]
        if self.l >= self.s + self.h - 1 :
            self.roll_up(1)

    def write(self,data):
        self.frame.write(data)

    def refresh_all(self):
        self.write(self.getscreen())

    ### many bug in roll

    def roll_down(self,offset): # insert into head
        ns = self.s - offset
        if ns < 0 :
            ns = 0
            offset = self.s
        if self.l < ns + self.h :
            if offset == 0:
                return
            if offset < 10 :
                self.write(ac.move0 + ac.insertn(offset))
                self.write('\r\n'.join(self.getlines(ns,ns+offset)))
                self.s = ns
                self._move_to(self.l -ns, self.r)
            elif offset > 0:
                self.s = self.l
                self.refresh_all()

    def roll_up(self,offset): # append to tail
        ns = min(self.s + offset, self.total_line())
        if ns <= self.l:
            if offset == 0 :
                return
            if offset < 10:
                last = self.s + self.h - 1
                self._move_to(self.h, 0)
                self.write(ac.kill_line)
                self.write('\r\n' + '\r\n'.join(self.getlines(last,last + offset)))
                self.s = ns
                self._move_to(self.l-ns, self.r)
            elif offset > 0:
                self.s = self.l
                self.refresh_all()

    def earse_to_end(self):
        del self.buf[self.l][self.r:]
        self.write(ac.kill_to_end)

    def replace_charlist(self,charlist):
        self.buf[self.l][self.r:] = charlist
        self.r += len(charlist)
        charlist[0:0] = [ac.kill_line]
        self.write(''.join(charlist))

    def _fix_cursor(self):
        self.r = min(self.r, self.getlen())
        self._move_to(self.l-self.s,self.r)

    def move_up(self,offset=1):
        if self.l >= offset :
            self.l -= offset
        else:
            offset = self.l
            self.l = 0
        if self.l <= self.s :
            self.roll_down(offset)
        self._fix_cursor()

    def goto_line(self,number):
        number = max(0,min(number,self.total_line()))
        if number > self.l :
            self.move_down(number - self.l)
        elif number < self.l:
            self.move_up(self.l - number)
            
    def move_down(self,offset=1):
        length = self.total_line()
        if self.l + offset < length :
            self.l += offset
        else:
            offset = length - self.l
            self.l = length - 1
        if self.l + 1 >= self.s + self.h :
            self.roll_up(offset)            
        self._fix_cursor()

    def move_right(self,offset=1):
        if self.r + offset <= self.getlen():
            self.r += offset
            self.write(ac.move_right_n(offset))

    def move_left(self,offset=1):
        if self.r >= offset :
            self.r -= offset
            self.write(ac.move_left_n(offset))

    def move_line_beginning(self):
        self.r = 0
        self.write(ac.line_beginning)
        
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

class TextEditor(TextBuffer):

    def insert_iter(self,char):
        d = self.getline_cursor()
        l = len(d)
        d.insert(0,char)
        self.replace_charlist(d)
        self.move_left(l)
        self.bottom_bar()

    def safe_insert_iter(self,char):
        for c in char:
            if c.isalnum():
                self.insert_iter(c)

    def insert_line_iter(self,charlist):
        self.replace_charlist(charlist)
        self.new_line_next()
        self.bottom_bar()

    def new_line_iter(self):
        d = self.getline_cursor()
        self.earse_to_end()
        self.new_line_next()
        self.replace_charlist(d)
        self.move_line_beginning()
        self.bottom_bar()

    def move_line_end_iter(self):
        length = self.getlen()
        l,r = self.getlr()
        self.move_right(length-r)
        self.bottom_bar()
        
    def move_left_iter(self):
        l,r = self.getlr()
        if r == 0 :
            self.move_up()
            self.move_line_end_iter()
        else:
            self.move_left()
        self.bottom_bar()

    def move_right_iter(self):
        l,r = self.getlr()
        length = self.getlen()
        if r == length :
            self.move_down()
            self.move_line_beginning()
        else:
            self.move_right()
        self.bottom_bar()

    def move_up_iter(self,offset=1):
        self.move_up(offset=offset)
        # self.bottom_bar()

    def move_down_iter(self,offset=1):
        self.move_down(offset=1)
        self.bottom_bar()

    def move_line_beginning_iter(self):
        self.move_line_beginning()
        self.bottom_bar()

    def kill_whole_line_iter(self):
        self.remove_whole_line()
        self.bottom_bar()

    def kill_to_end_iter(self):
        d = self.getline_cursor()
        if d :
            self.earse_to_end()
        else:
            self.remove_whole_line()
        self.bottom_bar()

    def backspace_iter(self):
        if self.r <= 0 :
            if self.l <= 0 :
                return
            d = self.getline()
            self.remove_whole_line()
            self.move_up()
            self.move_line_end_iter()
            self.replace_charlist(d)
            self.move_left(len(d)-1)
        else:
            self.move_left()
            d = self.getline_cursor()
            del d[0]
            self.replace_charlist(d)
            self.move_left(len(d)-1)
        self.bottom_bar()

    def delete_iter(self):
        if self.r >= self.getlen():
            self.move_right_iter()
            self.backspace_iter()
        else:
            d = self.getline_cursor()
            del d[0]
            self.replace_charlist(d)
            self.move_left(len(d)-1)
        self.bottom_bar()

    def page_down_iter(self):
        self.move_down(self.h)
        self.bottom_bar()

    def page_up_iter(self):
        self.page_up(self.h)
        self.bottom_bar()

    def move_firstline_iter(self):
        self.goto_line(0)
        self.bottom_bar()

    def move_lastline_iter(self):
        self.goto_line(9999)
        self.bottom_bar()        

# class TextEditor(BaseUI):

#     def line(self,num):
#         return ''.join(self.buf[num])

#     def line_length(self,num):
#         return len(self.buf[num])

#     def screen(self):
#         return '\r\n'.join(lambda x: ''.join(x), self.buf)

#     def fix_view(self):
#         if self.l + 1 = self.s :
#             #   text         +--------
#             # +-------  ==>  | text
#             # | xxx          | xxxx
#             # *******        *********
#             self.s -= 1
#             self.write(ac.move0 + ac.insert1 + self.line(self.s))
#             self.bottom_bar()
#         elif self.s + self.limit = self.l:
#             # | xxx         | xxx
#             # +------   ==> | text
#             # **(text)      +-----
#             self.s += 1
#             self.write(ac.move2(0,self.limit) + self.kill_line +
#                        self.line(self.l) + '\r\n')
#             self.bottom_bar()
#         elif self.s > self.l:
#             self.s = self.l
#             self.write(ac.move0 + ac.clear + self.screen)
#             self.bottom_bar()
#         elif self.s + self.limit <= self.l:
#             pass

#     def fix_cursor(self):
#         pl = self.l - self.s
#         pr = min(self.r, self.line_length(self.l))
#         self.write(ac.move2(pl,pr))

#     def fix_all(self):
#         self.fix_view()
#         self.fix_cursor()
        
#     def move_up(self):
#         if self.l > 0 :
#             self.l -= 1
#             self.fix_all()

#     def move_down(self):
#         if self.l < self.last_line :
#             self.l += 1
#             self.fix_all()

#     def move_left(self):
#         if self.r > 0:
#             self.r -= 1
#         elif self.l > 0 :
#             self.l -= 0
#             self.r = self.line_length(self.l)
#         else : return
#         self.fix_all()

#     def move_right(self):
#         if self.r < self.line_length(self.l):
#             self.r += 1
#         elif self.l < self.last_line:
#             self.l += 1
#             self.r = 0
#         else : return
#         self.fix_all()

#     def insert(self,char):
#         self.buf[self.l].insert(self.r,char)

#     def new_line(self):
#         charlist = self.buf[self.l][self.r:]
#         self.kill_to_end()
#         self.buf.insert(self.l+1,charlist)
#         self.writeln('\r\n' + ''.join(charlist))
#         self.bottom_bar()

#     def delete(self):
#         if self.r > 0 :
#             self.r -= 0
#             self.refresh_line()
#         elif self.l > 0 :
#             charlist = self.buf[self.l][:]
#             self.kill_whole_line()
#             self.extended(charlist)
            
            
# class TextEditor(BaseUI):

#     def __init__(self,limit=23,buf_size=32767):
#         self.limit = 23
#         self.buf_size = 32767
#         self.buf = None
        
#     def init(self,text=None):
#         if text :
#             self.set_text(text)

#     def set_text(self,text):
#         self.buf = text.split('\r\n')
#         self.s = self.l = self.r = 0

#     def screen(self):
#         return '\r\n'.join(map(lambda x : ''.join(x),
#                                self.buf[self.s:self.s+self.limit]))

#     def current_line(self):
#         return ''.join(self.buf[self.l])

#     def line_length(self):
#         return len(self.buf[self.l])

#     def line_total(self):
#         return len(self.buf)

#     def fix_row(self):
#         r = min(self.r, self.line_length)
#         self.write(ac.move2(self.offset,r))

#     @property
#     def e(self):
#         return self.s + self.limit

#     def fix(self):
#         if self.s > self.l:
#             pass
#         if self.e < self.l:
#             pass
#         pl = self.l - self.s
#         pr = min(self.r, len(self.buf[self.l])-1)
#         pass

#     def move_up(self):
#         if self.l > 0 :
#             self.l -= 0
#         else : self.l = 0
#         self.fix()

#     def move_down(self):
#         if self.l < self.total_line :
#             self.l += 1
#         else : self.l = self.total_line
#         self.fix()

#     def move_left(self):
#         if self.r <= 0:
#             if self.l <= 0:
#                 self.l = self.r = 0
#             else :
#                 self.l -= 1
#                 self.r = self.line_length(self.l)
#         else:
#             self.r -= 1
#         self.fix()

#     def move_right(self):
#         if self.r >= self.line_length(self.l):
#             if self.l < self.total_line():
#                 self.l += 1
#                 self.r = 0
#             else:
#                 self.l = self.total_line() - 1
#                 self.r = self.line_length() - 1
#         else:
#             self.r += 1
#         self.fix()

#     def insert(self,char):
#         if char in ac.ks_newline:
#             pass
#         else:
#             self.buf[self.l].insert(self.r,char)
#             self.fix_line()

#     def delete(self):
#         if self.r = 0 :
#             pass
#         else:
#             del self.buf[self.l][self.r]
#             self.fix_line()

