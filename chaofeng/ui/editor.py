from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import datetime

__metaclass__ = type

class TextEditor(BaseUI):

    def escape(self, text):
        assert isinstance(text, unicode)
        return text.replace(u'\x1b', u'*')

    def init(self, text=None, hover_row=0, hover_col=0, vis_start=0, height=23):
        if text :
            buf = map(list, self.escape(text).split('\r\n')) + []
            self.buf = buf
        else:
            self.buf = [[]]
        self._hover_row = hover_row
        self._hover_col = hover_col
        self._vis_row = vis_start
        self.height = height

    def write(self, text):
        # raw_input(': '+repr(text))
        self.frame.write(text)

    def bottom_bar(self):
        self.write((ac.move2(self.height+1, 1) + ac.kill_line +
                    '[%d,%d]' % (self._hover_row ,self._hover_col)))
        self.fix_cursor()

    def restore_screen(self):
        buf = map(lambda x:''.join(x),
                  self.buf[self._vis_row:self._vis_row+self.height])
        self.write(''.join([
                    ac.move0,
                    ac.clear,
                    '\r\n'.join(buf),
                    '\r\n~' * (self.height - len(buf)),
                    ]))
        self.bottom_bar()

    def char_width(self, char):
        return ac.srcwidth(char)

    def visible_width(self):
        return reduce(lambda acc,obj: acc+self.char_width(obj),
                      self.buf[self._hover_row][:self._hover_col],1)

    def total_line(self):
        return len(self.buf)

    def line_length(self):
        return len(self.buf[self._hover_row])

    def fix_cursor(self):
        self._hover_col = min(self._hover_col, 78, len(self.buf[self._hover_row]))
        self._vis_ls = self.visible_width()
        self.write(ac.move2(self._hover_row - self._vis_row +1, self._vis_ls))

    def move_up(self):
        if self._hover_row:
            if self._hover_row > self._vis_row:
                self._hover_row -= 1
            else:
                self._vis_row -= 1
                self._hover_row = self._vis_row
                self.write(''.join([ac.move0, ac.insert1, '\r',
                                    ''.join(self.buf[self._vis_row])]))
                self.bottom_bar()
            self.fix_cursor()

    def move_down(self):
        if self._hover_row+1 < self.total_line():
            if self._hover_row+1 < self._vis_row + self.height:
                self._hover_row += 1
            else:
                self._vis_row += 1
                self._hover_row = self._vis_row + self.height - 1
                self.write(''.join(['\r\n', ac.kill_line, 
                                    ''.join(self.buf[self._hover_row]),
                                    '\r\n']))
                self.bottom_bar()
            self.fix_cursor()

    def move_right(self):
        length = len(self.buf[self._hover_row])
        if self._hover_col < length:
            char = self.buf[self._hover_row][self._hover_col]
            self._hover_col += 1
            char_width = self.char_width(char)
            self.write(ac.move_right_n(char_width))
        else:
            if self._hover_row +1 < self.total_line():
                self._hover_col = 0
                self.move_down()

    def move_left(self):
        if self._hover_col:
            self._hover_col -= 1
            char = self.buf[self._hover_row][self._hover_col]
            char_width = self.char_width(char)
            self.write(ac.move_left_n(char_width))
        else:
            if self._hover_row :
                self._hover_col = len(self.buf[self._hover_row-1])
                self.move_up()

    def insert_char(self, char):
        assert isinstance(char, unicode)
        if self._hover_col == self.line_length() :
            self.buf[self._hover_row].append(char)
            self._hover_col += 1
            self.write(char)
        else:
            self.buf[self._hover_row].insert(self._hover_col, char)
            self.write(''.join(self.buf[self._hover_row][self._hover_col:]))
            self._hover_col += 1
            self.fix_cursor()

    def restore_screen_remain(self):
        buf = map(lambda x:''.join(x),
                  self.buf[self._hover_row+1:self._vis_row+self.height])
        self.write(''.join([ac.clear1, ''.join(self.buf[self._hover_row][self._hover_col:]),
                            '\r\n' if buf else '', '\r\n'.join(buf),
                            '\r\n~'*(self._vis_row + self.height - self._hover_row -1 - len(buf) )]))
        self.fix_cursor()

    def delete(self):
        if self._hover_col < self.line_length() :
            self.buf[self._hover_row][self._hover_col:self._hover_col+1] = []
            self.write(''.join([ac.kill_line,
                        ''.join(self.buf[self._hover_row][self._hover_col:]),
                        ]))
            self.fix_cursor()
        else:
            if self._hover_row+1 < self.total_line():
                self.buf[self._hover_row].extend(self.buf[self._hover_row+1])
                self.buf[self._hover_row+1:self._hover_row+2] = []
                self.restore_screen_remain()

    def backspace(self):
        if self._hover_col or self._hover_row:
            self.move_left()
            self.delete()

    def new_line(self):
        if self._hover_col < self.line_length() :
            buf = self.buf[self._hover_row][self._hover_col:]
            del self.buf[self._hover_row][self._hover_col:]
            self.buf.insert(self._hover_row+1, buf)
            self._hover_col = 0
            self._hover_row += 1
            if self._hover_row < self._vis_row + self.height:
                self.write(''.join([ac.kill_to_end, '\r\n', ac.insert1, ''.join(buf)]))
            else:
                self._vis_row += 1
                self.write(''.join([ac.kill_to_end, '\r\n', ac.kill_line, ''.join(buf), '\r\n']))
        else:
            self._hover_row += 1
            self._hover_col = 0
            self.buf.insert(self._hover_row, [])
            if self._hover_row < self._vis_row + self.height:
                self.write(''.join(['\r\n', ac.insert1]))
            else:
                self._vis_row += 1
                self.write(''.join(['\r\n', ac.kill_line, '\r\n']))
        self.bottom_bar()
        self.fix_cursor()

    def kill_to_end(self):
        if self._hover_col == self.line_length():
            self.delete()
        else:
            del self.buf[self._hover_row][self._hover_col:]
            self.write(ac.kill_line)

    def move_beginning_of_line(self):
        self._hover_col = 0
        self.write('\r')

    def move_end_of_line(self):
        self._hover_col = self.line_length()
        self.fix_cursor()

    def goto(self, hover_row, hover_col=0):
        self._vis_row = max(min(self.total_line()-20, hover_row-10), 0)
        self._hover_row = hover_row
        self._hover_col = hover_col
        self.restore_screen()
        self.fix_cursor()

    def fix_range(self, *points):
        max_row_index = self.total_line() - 1
        buf = []
        for (row, col) in points:
            row = max(0, min(max_row_index, row))
            col = max(0, min(len(self.buf[row])-1, col))
            buf.append((row, col))
        return buf

    def safe_goto(self, hover_row, hover_col):
        hover_row = max(0, min(self.total_line()-1, hover_row))
        hover_col = max(0, min(self.line_length(), hover_col))
        if self._vis_row <= hover_row < self._vis_row + self.height:
            self._hover_row = hover_row
            self._hover_col = hover_col
            self.fix_cursor()
        else:
            self.goto(hover_row, hover_col)
        
    def restore_hover_line(self):
        self.goto(self._hover_row,  self._hover_col)

    def goto_beginning_of_file(self):
        self._hover_row = self._hover_col = self._vis_row = 0
        self.restore_screen()

    def goto_end_of_file(self):
        self._hover_row = self.total_line() - 1
        self._vis_row = max(self._hover_row - self.height, 0)
        self._hover_col = 0
        self.restore_screen()

    def insert_style(self):
        self.insert_char(u'*')

class TextEditorAreaMixIn:

    def set_mark(self):
        self.old_row = self._hover_row
        self.old_col = self._hover_col

    def exchange_pos(self):
        try:
            self.old_row
        except AttributeError:
            self.old_row = self.old_col = 0
        row, col = self._hover_row, self._hover_col
        self.goto(self.old_row, self.old_col)
        self.old_row, self.old_col = row, col

    def get_pair(self):
        try:
            self.old_row
        except AttributeError:
            self.old_row = self.old_col = 0
        if self.old_row < self._hover_row or \
                (self._hover_row==self.old_row and self.old_col < self._hover_col):
            return (self.old_row, self.old_col), (self._hover_row, self._hover_col)
        else:
            return (self._hover_row, self._hover_col), (self.old_row, self.old_col)

    def remove_area(self):
        (min_row, min_col), (max_row, max_col) = self.fix_range(*self.get_pair())
        self.safe_goto(min_row, min_col)
        if min_row == max_row:
            del self.buf[min_row][min_col:max_col]
            self.write(''.join([ac.kill_to_end, ''.join(self.buf[min_row][min_col:])]))
        else:
            del self.buf[max_row][:max_col]
            del self.buf[min_row+1:max_row]
            del self.buf[min_row][min_col:]
            self.restore_screen_remain()
        self.fix_cursor()
