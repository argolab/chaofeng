from baseui import BaseUI
import chaofeng.ascii as ac

class BigEditor(BaseUI):

    height = 23
    page_width = 75
    
    def escape(self, text):
        assert isinstance(text, unicode)
        return text.replace(u'\x1b', u'*')

    def init(self, text, row):
        if text:
            self.buf = map(list, self.escape(text).split('\r\n')) + []
        else:
            self.buf = [[]]
        self._hover_row = row
        self._hover_col = 0
        self.set_fpoint(row, 0)

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
        return 0
    
    def restore_screen(self):
        row = self._fix_row
        width = self._fix_width
        text = self.get_text_area(self._fix_row, self._fix_width, self.height, self.page_width,
                             buf=[ac.move0, ac.clear])
        self.write(text)
        start_index = self.get_line_start_index(self._hover_row, self._fix_width)
        print ('sindex', start_index)
        prebuf = self.buf[self._hover_row][start_index:self._hover_col]
        self._line_offset = self.visible_width(prebuf)

    def fix_cursor(self):
        self.write(ac.move2(self._hover_row - self._fix_row + 1, self._line_offset + 1))

    def set_fpoint(self, row, width):
        self._fix_row = row
        self._fix_width = width

    def move_left(self):
        if self._hover_col :
            self._hover_col -= 1
            char_width = self.char_width(self.get_hover())
            self._line_offset -= char_width
            if self._line_offset < 0 :
                self.set_fpoint(self._fix_row, self._fix_width-self.page_width)
                self.restore_screen()
            self.fix_cursor()

    def move_right(self):
        if self._hover_col < len(self.buf[self._hover_row]):
            char_width = self.char_width(self.get_hover())
            self._line_offset += char_width
            self._hover_col += 1
            if self._line_offset >= self.page_width :
                self.set_fpoint(self._fix_row, self._fix_width+self.page_width)
                self.restore_screen()
            self.fix_cursor()

    def move_point(self, row, col):
        # same fix_row
        self._hover_row = row
        self._hover_col = max(0, min(col, len(self.buf[row])))
        cur_width = self.visible_width(self.buf[self._hover_row][:self._hover_col])
        r,l = divmod(cur_width, self.page_width)
        if cur_width < self._fix_width :
            self.set_fpoint(self._fix_row, cur_width - l)
            self.restore_screen()
        elif cur_width > self._fix_width + self.page_width  :
            self.set_fpoint(self._fix_row, cur_width - l)
            self.restore_screen()
        else:
            self._line_offset = cur_width - self._fix_width
        self.fix_cursor()

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
        if self._hover_row+2 < self.total_line():
            if self._hover_row +1 == self._fix_row + self.height :
                self.fix_down()
            self.move_point(self._hover_row + 1, self._hover_col)

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
        pass

    def insert_char(self, char):
        self.buf[self._hover_row].insert(self._hover_col, char)
        self._line_offset += self.char_width(char)
        self._hover_col += 1
        if self._line_offset >= self.page_width:
            self.set_fpoint(self._fix_row, self._fix_width+self.page_width)
            self.restore_screen()
        else:
            self.restore_line_remain()
        self.fix_cursor()

    def poo(self):
        print self.get_hover()
