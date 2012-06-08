from baseui import BaseUI
import chaofeng.ascii as ac

class TextBuffer(BaseUI):

    key_maps = {}

    def __init__(self,limit=23):
        self.limit = limit

    def init(self):
        self.buf=[[]]
        self.l = 0
        self.r = 0
        self.s = 0

    def new_line(self):
        self.buf[self.l:self.l]=[[]]
        self.r = 0
        self.write('\r' + ac.insert1)

    def delete_line(self):
        del self.buf[self.l]
        # self.write(self.buf[self.l:

    def total_line(self):
        return len(self.buf)

    def new_line_next(self):
        self.buf[self.l+1:self.l+1]=[[]]
        self.r = 0
        self.write('\n\r' + ac.insert1)

    def write(self,data):
        self.frame.write(data)

    def earse_to_end(self):
        del self.buf[self.l][self.r:]
        self.write(ac.kill_to_end)

    def replace_charlist(self,charlist):
        self.buf[self.l][self.r:] = charlist
        self.r += len(charlist)
        self.write(''.join(charlist))

    def move_up(self,offset=1):
        if self.l >= self.offset :
            self.l -= offset
            self.write(ac.move_up_n(offset))

    def move_down(self,offset=1):
        if self.l + offset < self.total_line() :
            self.l += offset
            self.write(ac.move_down_n(offset))

    def move_right(self,offset=1):
        if self.r + offset <= len(self.getline()):
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

    def getscreen(self):
        return '\r\n'.join(lambda x: ''.join(x),self.buf)

    def replace(self,char):
        self.buf[self.l][self.r] = char
        self.write(char)

class TextEditor(TextBuffer):

    def insert_iter(self,char):
        d = self.getline_cursor()
        d.insert(0,char)
        self.replace_charlist(d)
        self.move_left(len(d)-1)

    def new_line_iter(self):
        d = self.getline_cursor()
        self.earse_to_end()
        self.move_down()
        self.new_line()
        self.replace_charlist(d)

    def move_line_end_iter(self):
        length = len(self.getline())
        l,r = self.getlr()
        print length
        print r
        self.move_right(length-r)
        
    def move_left_iter(self):
        l,r = self.getlr()
        if r == 0 :
            self.move_up()
            self.move_line_end_iter()
        else:
            self.move_left()

    def move_right_iter(self):
        l,r = self.getlr()
        length = len(self.getline())
        if r == length :
            self.move_down()
            self.move_line_beginning()
        else:
            self.move_right()

    def move_up_iter(self):
        self.move_up()

    def move_down_iter(self):
        self.move_down()

    def move_line_beginning_iter(self):
        self.move_line_beginning()

    def kill_whole_line_iter(self):
        self.remove_whole_line()

    def kill_to_end_iter(self):
        d = self.getline_cursor()
        if d :
            self.kill_to_end()
        else:
            self.remove_whole_line()

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

