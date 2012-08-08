from baseui import BaseUI
import chaofeng.ascii as ac
from datetime import datetime

class TextEditor(BaseUI):

    def init(self, text=None, hover_row=0, hover_col=0, vis_start=0):
        if text :
            buf = map(list, text.split('\r\n')) + []
            self.buf = buf
        else:
            self.buf = [[]]
        self._hover_row = hover_row
        self._hover_col = hover_col
        self._vis_start = vis_start

    def bottom_bar(self):
        self.write((ac.move2(self.h+1, 0) + ac.kill_line +
                    '[%d,%d] %s' % (self.l,self.r, ''.join(self.getline())[:80])))
        self.fix_cursor()

    def restore_screen(self):
        buf = self.buf[self._hover_row:self._hover_row+self.height]
        self.write(''.join([
                    ac.move0,
                    ac.clear,
                    '\r\n'.join(buf),
                    ]))
        self.bottom_bar()

    def char_width(self, char):
        return len(char)

    def visible_width(self):
        return reduce(lambda acc,obj: acc+self.char_width(obj),
                      self.buf[self._hover_row][:self._hover_col],1)

    def fix_cursor(self):
        self._hover_col = min(self._hover_col, len(self.buf[self._hover_row]))
        cr = self.visible_width()
        self.write(ac.move2(self._hover_col - self._vis_start +1), cr)

