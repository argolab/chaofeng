import chaofeng.ascii as ac
from baseui import BaseUI
from collections import deque

class BaseBuffer(BaseUI):

    '''
    Loader is a function that like loader(start_line, limit),
    which will load [start_line:start_line+limit]

    @vis_height : the visable height line in screen
    @current    : current lines buffer display in screen
    @bufstr     : current text in screen
    
    '''

    seq_lines = '\r\n'+ac.kill_line
    empty_line = seq_lines

    def init(self):
        raise Exception('Cannot instance a basebuffer')

    def init_buf(self, loader, start_num, start_line, page_limit=20):
        '''
        Init the buf. It should be called before everything.
        '''
        self.start_line = start_line
        self.page_limit = page_limit
        self.loader = loader
        self.set_page_start(start_num)

    def fetch(self):
        return self.current

    def get_screen(self):
        return ''.join((ac.move2(self.start_line, 1),
                        self.seq_lines.join(self.current),
                        self.empty_line*(self.page_limit-self.vis_height)))

    def restore_screen(self):
        self.frame.write(self.bufstr)

    def set_page_start(self, start_num):
        '''
        Set the start_num as the first display line in the screen.
        If start_num<0 , it'wll display 0 as first line.
        If can't fetch any line, return False else return True.
        '''
        if start_num < 0 : start_num = 0
        current = self.loader(start_num, self.page_limit)
        if current :
            self.start_num = start_num
            self.vis_height = len(current)
            self.current = current
            self.bufstr = self.get_screen()
            return True
        else : return False
        
    def set_page_start_lazy_iter(self, start_num):
        if start_num < 0 : start_num = 0
        if start_num == self.start_num:
            return True
        if self.set_page_start(start_num) :
            self.restore_screen()
            return True
        else : return False

    def restore_screen(self):
        '''
        Restore the buffer, display it in screen.
        Notice that it will not reload the data, it just
        print the buffer's cache in buffstr.
        '''
        self.frame.write(ac.move2(self.start_line, 1) + ac.kill_line + \
                              ('\r\n'+ac.kill_line).join(self.current))

    def page_prev_iter(self):
        '''
        Set previous page as display. Return True while has at least one line,
        or return False while cannot fetch any things.
        '''
        return self.set_page_start_lazy_iter(self.start_num - self.page_limit)

    def page_next_iter(self):
        '''
        Set the next page as display. Return True while has fetch something,
        or return Flase whie it's out of range.
        '''
        return self.set_page_start_lazy_iter(self.start_num + self.page_limit)

    def go_first_iter(self):
        return self.set_page_start_lazy_iter(0)

class PagedTable(BaseBuffer):

    def init(self, loader, formater, start_num, start_line, page_limit=20):
        self.reset_loader(loader, formater)
        self.init_buf(self.get_wrapper, start_num, start_line, page_limit)
        self.hover = -1
        self.reset_cursor(start_num % page_limit)

    def reset_loader(self, loader, formater):
        self.table_loader = loader
        self.formater = formater

    def get_wrapper(self, start, limit):
        self.tabledata = self.table_loader(start, limit)
        return map(self.formater, self.tabledata)

    def reset_cursor(self, hover):
        if hover < 0 : hover = 0
        if hover < self.vis_height :
            self.hover = hover
            return True
        else : return False

    def restore_cursor(self):
        self.frame.write(ac.move2(self.start_line + self.hover, 1)
                         + '>')

    def reset_cursor_iter(self, hover):
        if self.reset_cursor(hover):
            self.frame.write(ac.movex_d + ' ' + ac.move2(self.start_line + self.hover, 1)
                             + '>')

    def restore_screen(self):
        super(PagedTable, self).restore_screen()
        self.restore_cursor()

    def page_prev_iter(self):
        super(PagedTable, self).page_prev_iter() and\
            (self.hover >= self.vis_height) and \
            self.reset_cursor_iter(self.vis_height-1)

    def page_next_iter(self):
        if super(PagedTable, self).page_next() :
            self.reset_cursor_iter(min(self.hover, self.vis_height-1))
        else:
            self.reset_cursor_iter(self.vis_height)

    def move_up_iter(self):
        if self.hover < 0 :
            self.hover = 0
        elif self.hover > 0:
            self.reset_cursor_iter(self.hover-1)

    def move_down_iter(self):
        if self.hover+1 <= self.vis_height :
            self.reset_cursor_iter(self.hover + 1)
        else:
            super(PagedTable, self).page_next_iter() and\
                self.reset_cursor_iter(0)

    def goto_iter(self, num):
        s, h = divmod(num, self.vis_height)
        self.set_page_start_iter(s) and\
            self.reset_cursor_iter(h)
