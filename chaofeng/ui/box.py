from baseui import BaseUI
import chaofeng.ascii as ac
from chaofeng import sleep
from eventlet import spawn as lanuch
from itertools import cycle
from uiexception import NullValueError, TableLoadNoDataError

class BaseTextBox(BaseUI):
    pass

class Animation(BaseTextBox):

    '''
    Call back self.frame.play_done wher playone is True.
    data :: [ (text, time) ... ]
    '''

    def init(self, data, start_line, pause=None, callback=None):
        self.data = data
        self.len = len(self.data)
        self.start_line = start_line
        self.pause = pause
        self.callback = callback

    def write(self, data):
        self.frame.write(''.join((ac.save,
                                  ac.move2(self.start_line, 1),
                                  data,
                                  ac.reset,
                                  ac.restore)))
        
    def prepare(self, playone=False):
        if playone:
            self.gener = iter(self.data)
        else:
            self.gener = cycle(self.data)
            
    def clear(self):
        if hasattr(self,'thread') :
            self.thread.kill()

    def goto_one(self):
        while True:
            try:
                data, time = self.gener.next()
            except StopIteration:
                data = None
            if data is None:
                self.callback()
                return
            self.write(data)
            if time is True:
                self.pause()
            elif time is False:
                self.callback()
                return
            else:
                sleep(time)

    def run(self, playone=False):
        self.prepare(playone)
        while True :
            self.goto_one()

    def launch(self, playone=False):
        self.thread = lanuch(self.run, playone)

class LongTextBox(BaseTextBox):

    height = 23
    
    def init(self, lines, callback):
        self.lines = lines
        self._vis_start = 0
        self.callback = callback

    def reset_lines(self, lines):
        self._vis_start = 0
        self.lines = lines
        
    def set_start(self, start):
        try:
            self.lines[start]
        except IndexError:
            return
        self._vis_start = start

    def restore_screen(self):
        self.frame.write(''.join([ac.move0 , ac.clear,
                                 '\r\n'.join(self.lines[self._vis_start:self._vis_start+self.height])]))
        self.frame.write('\r\n')
        
    def move_up(self):
        if self._vis_start :
            self._vis_start -= 1
            self.frame.write(''.join([ac.move0 , ac.insert1 ,
                                self.lines[self._vis_start]]))
        else:
            self.callback(False)

    def move_down(self):
        try:
            line = self.lines[self._vis_start+self.height]
        except IndexError:
            self.callback(True)
            return
        self._vis_start += 1
        self.frame.write(''.join([ac.move2(self.height+1, 1), ac.kill_line,
                            line, '\r\n']))

    def goto_line(self, num):
        try:
            self.lines[num]
        except IndexError:
            return
        self._vis_start = start
        self.restore_screen()

    def goto_first(self):
        self._vis_start = 0
        self.restore_screen()

    def page_down(self):
        self.goto_line(self._vis_start + self.height)

    def page_up(self):
        self.goto_line(self._vis_start - self.height)

class SimpleTextBox(BaseTextBox):

    '''
    Widget for view long text.
    When user try move_up in first line, callback(False)
    will be called, and callback(True) will be when
    move_down in last lin.
    '''

    def init(self, text, callback, height=23):
        self.h = height
        self.set_text(text)
        self.callback = callback
        
    def set_text(self,text):
        self.buf = text.splitlines()
        self.s = 0
        self.len = len(self.buf)
        self.max = max(0,self.len - self.h)

    reset = set_text

    def getscreen(self):
        return '\r\n'.join(self.getlines(self.s, self.s+self.h))

    def getscreen_with_raw(self):
        buf = self.getlines(self.s, self.s+self.h)
        return ('\r\n'.join(buf), buf)
        
    def getlines(self,f,t):
        if t > self.len :
            return self.buf[f:t]+['~',]*(t-self.len)
        else:
            return self.buf[f:t]

    def fix_bottom(self):
        pass

    def set_start(self,start):
        if start == self.s:
            return
        if (self.s > start) and (self.s <= start + 10):
            offset = self.s - start
            self.write(ac.move0 + ac.insertn(offset) + '\r')
            self.write('\r\n'.join(self.getlines(start,self.s)))
            self.s = start
            self.fix_bottom()
        elif (start > self.s) and (start <= self.s + 10):
            astart = self.s + self.h # Append Start
            self.write(ac.move2(self.h+1,0))
            self.write(ac.kill_line)
            self.write('\r\n'.join(self.getlines(astart, start + self.h)))
            self.write('\r\n')
            self.s = start
            self.fix_bottom()
        else :
            self.s = start
            self.restore_screen()

    def move_up(self):
        if self.s :
            self.set_start(self.s-1)
        else:
            self.callback(False)
            
    def move_down(self):
        if self.s + self.h < self.len:
            self.set_start(self.s+1)
        else:
            self.callback(True)

    def goto_line(self,num):
        # if self.s == 0 and num < 0 :
        #     self.callback(True)
        # if self.s == self.max and num > 0:
        #     self.callback(False)
        self.set_start(max(0,min(num,self.len-self.h)))

    def goto_first(self):
        self.goto_line(0)

    def goto_last(self):
        self.goto_line(self.len-self.h)

    def page_down(self):
        self.goto_line(self.s + self.h)

    def page_up(self):
        self.goto_line(self.s - self.h)

    def restore_screen(self):
        self.write(ac.move0 + ac.clear)
        self.write(self.getscreen())
        self.fix_bottom()
        
    def write(self,data):
        self.frame.write(data)

class ListBox(BaseUI):

    def init(self, start_line, height=20):
        self.height = height
        self.page_limit = height * 3
        self.start_line = start_line
        self.data = None
        self.text = None
        
    def fix_cursor(self):
        self.frame.write(ac.move2(self.row, self.col))

    def get_update_txt(self, text):
        row = self.start_line
        col = 5
        buf = []
        for d in text[:self.page_limit] :
            if col == 5 :
                buf.append('%s%s%s' % (ac.move2(row, col), ac.kill_to_end, d))
            else:
                buf.append('%s%s' % (ac.move2(row, col), d))
            col += 25
            if col >= 70:
                col = 5
                row += 1
        if row < self.start_line + self.height - 1:
            buf += ['\r\n' + ac.kill_line] * (self.start_line + self.height - 1 - row)
        return ''.join(buf)

    def fetch(self):
        return self.data[self.hover]

    def update(self, text, data):
        assert data
        self.data = data
        self.text = text
        self._set_start_item(0, 0, self.start_line, 4)
        self.fix_cursor()

    def _set_start_item(self, start, hover, row, col):
        self.start_item = start
        self.hover = hover
        self.col = col
        self.row = row
        # self.frame.write(ac.clear)
        self.frame.write(self.get_update_txt(self.text[start:start+self.page_limit]))

    def move_down(self):
        if self.hover + 3 < len(self.data) :
            if self.row +1 == self.start_line + self.height:
                self._set_start_item(self.start_item + self.page_limit,
                                     self.hover + 3, self.start_line, self.col)
            else:
                self.hover += 3
                self.row += 1
            self.fix_cursor()

    def move_up(self):
        if self.hover - 3 >= 0 :
            if self.row == self.start_line :
                self._set_start_item(self.start_item - self.page_limit,
                                     self.hover -3, self.start_line + self.height - 1, self.col)
            else:
                self.row -= 1
                self.hover -= 3
            self.fix_cursor()

    def move_left(self):
        if self.hover :
            if self.col - 25 > 0 :
                self.col -= 25
                self.hover -= 1
            elif self.row == self.start_line:
                self._set_start_item(self.start_item - self.page_limit,
                                     self.hover - 1, self.start_line + self.height -1,
                                     self.col + 50)
            else:
                self.col += 50
                self.row -= 1
                self.hover -= 1
            self.fix_cursor()

    def move_right(self):
        if self.hover +1 < len(self.data) :
            if self.col + 25 < 75:
                self.col += 25
                self.hover += 1
            elif self.row == self.start_line + self.height -1 :
                self._set_start_item(self.start_item + self.page_limit,
                                     self.hover + 1, self.start_line, self.col - 50)
            else:
                self.col -= 50
                self.row += 1
                self.hover += 1
            self.fix_cursor()
            
class PagedTable(BaseUI):

    seq_lines = '\r\n' + ac.kill_line
    empty_line = '\r\n' + ac.kill_line

    def init(self, loader, formater, start_num, start_line, height=20):
        '''
        start_num >= 0
        '''
        self.height = height
        self.start_line = start_line
        self.loader = loader
        self.formater = formater

        if start_num < 0 : start_num = 0
        r = start_num % self.height
        try:
            self.load_data(start_num - r)
        except TableLoadNoDataError:
            raise NullValueError
        self.hover = r
        
    def safe_set_cursor(self, hover):
        if hover < 0 : hover = 0
        if hover < self.index_limit:
            self.hover = hover
            return True
        else : return False

    def restore_cursor_gently(self):
        self.frame.write(u'%s>' % ac.move2(self.start_line + self.hover, 1))

    def _fix_cursor(self):
        self.frame.write('%s %s>' % (ac.movex_d,
                                     ac.move2(self.start_line + self.hover, 1)))

    def load_data(self, start_num):
        data = self.loader(start_num, self.height)
        if data :
            self.data = data
            self.start_num = start_num
            self.wrapper_data = [ self.formater(x) for x in self.data]
            self.index_limit = len(self.data)
            self._screen = ''.join([ac.move2(self.start_line, 1), ac.kill_line, 
                                    self.seq_lines.join(self.wrapper_data),
                                    self.empty_line*(self.height - self.index_limit)])
        else:
            raise TableLoadNoDataError

    def safe_load_data(self, start_num):
        if start_num < 0 :
            return False
        try:
            self.load_data(start_num)
        except TableLoadNoDataError:
            return False
        else:
            return True

    def restore_screen(self):
        self.frame.write(self._screen)
        self.restore_cursor_gently()
        
    def page_up(self):
        if self.safe_load_data(self.start_num - self.height) :
            self.restore_screen()

    def page_down(self):
        if self.safe_load_data(self.start_num + self.height) :
            self.restore_screen()
        else:
            self.hover = self.index_limit - 1
            self._fix_cursor()

    def move_up(self):
        if self.hover :
            self.hover -= 1
            self._fix_cursor()
        elif self.start_num and self.safe_load_data(self.start_num - self.height):
            self.hover = self.index_limit - 1
            self.restore_screen()

    def move_down(self):
        if self.hover+1 < self.index_limit :
            self.hover += 1
            self._fix_cursor()
        elif self.safe_load_data(self.start_num + self.index_limit) :
            self.hover = 0
            self.restore_screen()

    def goto(self, num):
        if num < 0:
            self.load_data(0)
            self.hover = 0
            self.restore_screen()
            return True
        r = num - num % self.height
        if self.safe_load_data(r) :
            self.hover = num - r
            self.restore_screen()

    def goto_first(self):
        if self.safe_load_data(0) :
            self.hover = 0
            self.restore_screen()

    def fetch(self):
        return self.data[self.hover]
        
    def fetch_num(self):
        return self.start_num + self.hover

    def set_hover_data(self, data):
        self.data[self.hover] = data
        self.frame.write(''.join(('\r',
                                  ac.kill_line,
                                  self.formater(data))))
        self.restore_cursor_gently()

    def is_empty(self):
        return self.index_limit > 0

    def reload(self):
        self.load_data(self.start_num)
        if self.hover >= self.index_limit:
            self.hover = self.index_limit - 1
