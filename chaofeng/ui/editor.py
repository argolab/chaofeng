#!/usr/bin/python2
# -*- coding: utf-8 -*-

from baseui import BaseUI
import chaofeng.ascii as ac

class TextEditor(BaseUI):

    height = 23
    page_width = 75

    def hint(self, msg):
        self.write(''.join([ac.move2(24,1),
                            ac.kill_line,
                            msg]))                            
        self.fix_cursor()
        
    def escape(self, text):
        assert isinstance(text, unicode)
        return text.replace(u'\x1b', u'*')

    def init(self, text, row):
        if text:
            if isinstance(text, list) :
                self.buf = text[:]
            else:
                self.buf = map(list, self.escape(text).split('\r\n')) + []
        else:
            self.buf = [[]]
        self._hover_row = row
        self._hover_col = 0
        # self.two_esc_mode = True
        self.set_fpoint(row, 0)

    def reset(self, text, row):
        self.init(text, row)
        self.restore_screen()
        
    def fetch_all(self):
        return '\r\n'.join(''.join(line) for line in self.buf)

    def fetch_lines(self):
        return [''.join(line) for line in self.buf]

    def char_width(self, char):
        return ac.srcwidth(char)

    def total_line(self):
        return len(self.buf)

    def write(self, data):
        self.frame.write(data)

    def visible_width(self, charlist):
        return reduce(lambda acc,obj : acc+self.char_width(obj),
                      charlist, 0)

    def get_text_area(self, row, offset_start, height, width, buf=None):
        buf = buf or []
        offset_limit = offset_start + width
        for r in range(row, min(row + height, self.total_line())):
            offset = 0
            for l in range(0, len(self.buf[r])):
                if offset >= offset_start :
                    buf.append(self.buf[r][l])
                offset += self.char_width(self.buf[r][l])
                if offset >= offset_limit:
                    break
            buf.append('\r\n')
        return ''.join(buf)

    def get_line_start_index(self, num, offset_start):
        offset = 0
        for l in range(0, len(self.buf[num])):
            if offset >= offset_start:
                return l
            offset += self.char_width(self.buf[num][l])
        return len(self.buf[num]) - 1
    
    def restore_screen(self):
        text = self.get_text_area(self._fix_row, self._fix_width, self.height, self.page_width,
                             buf=[ac.move0, ac.clear])
        self.write(text)
        start_index = self.get_line_start_index(self._hover_row, self._fix_width)
        prebuf = self.buf[self._hover_row][start_index:self._hover_col]
        self._line_offset = self.visible_width(prebuf)

    def fix_cursor(self):
        self.write(ac.move2(self._hover_row - self._fix_row + 1, self._line_offset + 1))

    def set_fpoint(self, row, width):
        self._fix_row = row
        self._fix_width = width

    def move_left(self):
        if (self._hover_col == 0) and (self._hover_row == 0) :
            return
        if self._hover_col == 0 :
            if self._hover_row == self._fix_row :
                self.fix_up()
            self.move_point(self._hover_row - 1, len(self.buf[self._hover_row-1]))
        else:
            self._hover_col -= 1
            char_width = self.char_width(self.get_hover())
            self._line_offset -= char_width
            if self._line_offset < 0 :
                self.set_fpoint(self._fix_row, self._fix_width-self.page_width)
                self.restore_screen()
            self.fix_cursor()

    def move_right(self):
        if self.is_last_line() and self.is_end_of_line() :
            return
        if self.is_end_of_line() :
            if self._hover_row +1 == self._fix_row + self.height :
                self.fix_down()
            self.move_point(self._hover_row + 1, 0)
        else:
            char_width = self.char_width(self.get_hover())
            self._line_offset += char_width
            self._hover_col += 1
            if self._line_offset >= self.page_width :
                self.set_fpoint(self._fix_row, self._fix_width+self.page_width)
                self.restore_screen()
            self.fix_cursor()

    def _move_point(self, row, col):
        fix_row = self._fix_row if (self._fix_row <= row < self._fix_row + self.height)\
            else row
        offset = self.visible_width(self.buf[row][:col])
        fix_width = self._fix_width if (self._fix_width <= offset < self._fix_width + self.page_width)\
            else offset - offset % self.page_width
        if (fix_row != self._fix_row) or (fix_width != self._fix_width):
            self.set_fpoint(fix_row, fix_width)
            self.restore_screen()
        else:
            self._line_offset = offset - fix_width
        self.fix_cursor()

    def move_point(self, row, col):
        # same fix_row
        self._hover_row = max(0, min(row, self.total_line()-1))
        self._hover_col = max(0, min(col, len(self.buf[row])))
        self._move_point(row, col)
            
    def get_hover(self):
        if self._hover_col < len(self.buf[self._hover_row]):
            return self.buf[self._hover_row][self._hover_col]
        else:
            return ' '

    def get_screen_line(self, num):
        try:
            self.buf[num]
        except IndexError:
            return '~'
        else:
            buf = []
            offset = 0
            width = self._fix_width
            width_limit = width + self.page_width
            for l in range(0, len(self.buf[num])):
                if offset >= width :
                    buf.append(self.buf[num][l])
                offset += self.char_width(self.buf[num][l])
                if offset >= width_limit:
                    break
            return ''.join(buf)

    def fix_up(self):
        # Remember to check if self._fix_row > 0
        self._fix_row -= 1
        self.write(''.join([ac.move0, ac.insert1, '\r', self.get_screen_line(self._fix_row)]))

    def fix_down(self):
        # Remember to check if self._fix_row +2 < len(self.buf)
        self.write(''.join([ac.move2(self.height+1, 0), ac.kill_line,
                            self.get_screen_line(self._fix_row + self.height), '\r\n']))
        self._fix_row += 1

    def move_up(self):
        if self._hover_row :
            if self._hover_row == self._fix_row :
                self.fix_up()
            self.move_point(self._hover_row - 1, self._hover_col)

    def move_down(self):
        if self._hover_row+1 < self.total_line():
            if self._hover_row +1 >= self._fix_row + self.height :
                self.fix_down()
            self.move_point(self._hover_row + 1, self._hover_col)

    def page_up(self):
        self.move_point(self._hover_row - self.height, self._hover_col)

    def page_down(self):
        self.move_point(self._hover_row + self.height, self._hover_col)

    def move_beginning_of_line(self):
        self.move_point(self._hover_row, 0)

    def move_end_of_line(self):
        self.move_point(self._hover_row, len(self.buf[self._hover_row]))

    def restore_line_remain(self):
        buf = [ac.kill_to_end]
        offset = self._line_offset
        offset_limit = self._fix_width + self.page_width
        for i in range(self._hover_col, len(self.buf[self._hover_row])):
            buf.append(self.buf[self._hover_row][i])
            offset += self.char_width(self.buf[self._hover_row][i])
            if offset >= offset_limit :
                break
        self.write(''.join(buf))

    def restore_screen_remain(self):
        self.restore_line_remain()
        text = self.get_text_area(self._hover_row+1, self._fix_width,
                                  self.height - 1 + self._fix_row - self._hover_row,
                                  self.page_width, buf=['\r\n', ac.clear1])
        self.write(text)
        self.fix_cursor()

    def insert_char(self, char):
        self.buf[self._hover_row].insert(self._hover_col, char)
        self._line_offset += self.char_width(char)
        if self._line_offset >= self.page_width:
            self.set_fpoint(self._fix_row, self._fix_width+self.page_width)
            self.restore_screen()
        else:
            self.restore_line_remain()
        self._hover_col += 1
        self.fix_cursor()

    def escape_charlist(self, string):
        return list(string)

    def insert_string(self, before, after):
        before = self.escape_charlist(before)
        after = self.escape_charlist(after)
        self.buf[self._hover_row][self._hover_col:self._hover_col] = before + after
        self._line_offset += reduce( lambda acc, d : acc + self.char_width(d),
                                     before, 0)
        if self._line_offset >= self.page_width:
            self.set_fpoint(self._fix_row, self._fix_width+self.page_width)
            self.restore_screen()
        else:
            self.restore_line_remain()
        self._hover_col += len(before)
        self.fix_cursor()
        
    def is_end_of_line(self):
        # print (self._hover_col, len(self.buf[self._hover_row]) , 'end_of_line')
        return self._hover_col == len(self.buf[self._hover_row])

    def is_last_line(self):
        return self._hover_row + 1 == len(self.buf)

    def merge_next_line(self):
        self.buf[self._hover_row].extend(self.buf[self._hover_row+1])
        del self.buf[self._hover_row+1]
        self.restore_screen_remain()

    def delete(self):
        if self.is_last_line() and self.is_end_of_line() :
            return
        if self.is_end_of_line() :
            self.merge_next_line()
        else :
            del self.buf[self._hover_row][self._hover_col]
            self.restore_line_remain()
        self.fix_cursor()

    def backspace(self):
        if self._hover_row or self._hover_col:
            self.move_left()
            self.delete()

    def kill_to_end(self):
        if self.is_end_of_line() and self.is_last_line():
            return
        if self.is_end_of_line() :
            self.merge_next_line()
        else:
            del self.buf[self._hover_row][self._hover_col:]
            self.write(ac.kill_to_end)

    def new_line(self):
        tmp = self.buf[self._hover_row][self._hover_col:]
        if tmp:
            del self.buf[self._hover_row][self._hover_col:]
            self.write(ac.kill_to_end)

        self.buf.insert(self._hover_row+1, tmp)
        self.move_beginning_of_line()

        if self._hover_row+1 == self._fix_row + self.height:
            self.move_down()
        else:
            self.write(''.join(['\r\n', ac.insert1]))
            self.move_down()
            self.restore_line_remain()
        self.fix_cursor()

    def move_beginning_of_file(self):
        self._fix_row = self._hover_row = self._hover_col = 0
        self.restore_screen()
        self.fix_cursor()

    def move_end_of_file(self):
        self._hover_row = self.total_line() - 1
        self._fix_row = max(0, self._hover_row-self.height+1)
        self._hover_col = 0
        self.restore_screen()
        self.fix_cursor()

    def restore_screen_iter(self):
        self.restore_screen()
        self.fix_cursor()

class TextEditorAreaMixIn:

    def fix_range(self, *points):
        max_row_index = self.total_line() - 1
        buf = []
        for (row, col) in points:
            row = max(0, min(max_row_index, row))
            col = max(0, min(len(self.buf[row])-1, col))
            buf.append((row, col))
        return buf

    def set_mark(self):
        self.old_row = self._hover_row
        self.old_col = self._hover_col

    def exchange_pos(self):
        try:
            self.old_row
        except AttributeError:
            self.old_row = self.old_col = 0
        row, col = self._hover_row, self._hover_col
        self.move_point(self.old_row, self.old_col)
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
        self.move_point(min_row, min_col)
        if min_row == max_row:
            res = ''.join(self.buf[min_row][min_col:max_col])
            del self.buf[min_row][min_col:max_col]
            self.write(''.join([ac.kill_to_end, ''.join(self.buf[min_row][min_col:])]))
        else:
            res = ''.join(self.buf[max_row][:max_col] +
                          self.buf[min_row+1:max_row] +
                          self.buf[min_row][min_col:])            
            del self.buf[max_row][:max_col]
            del self.buf[min_row+1:max_row]
            del self.buf[min_row][min_col:]
            self.merge_next_line()
        self.fix_cursor()
        return res

