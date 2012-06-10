import chaofeng.ascii as ac
from editor import TextEditorModule
from copy import deepcopy

class TextEditor_Cursor(TextEditorModule):
        
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

class TextEditor_Edit(TextEditorModule):

    def insert_iter(self,char):
        d = self.getline_cursor()
        l = len(d)
        d.insert(0,char)
        self.replace_charlist(d)
        self.move_left(l)

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

class TextEditor_Mark(TextEditorModule):

    @classmethod
    def __modinit__(cls):
        cls.add_hook("__init__","init_mark")

    def init_mark(self):
        self.set_mark_iter()
        self.clipboard =[[]]

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

class TextEditor_History(TextEditorModule):

    save_step_cmd = set(("kill_whole_line","kill_to_end","delete_iter",
                         "insert","new_line","backspace","delete"))

    save_force_cmd = set()

    @classmethod
    def __modinit__(cls):
        for cmd in cls.save_step_cmd:
            cls.add_hook(cmd,"save_cmd_step")
        for cmd in cls.save_force_cmd:
            cls.add_hook(cmd,"save_history")
        if hasattr(cls,"insert_iter"):
            cls.add_hook("insert","save_cmd_step_iter")
        cls._hislen = cls.kwargs['hislen']
        cls._dis = cls.kwargs['dis']
        cls.add_hook("__init__","init_history")

    def init_history(self):
        self.history = [[],]*10
        self._top = 0
        self._dd = 0

    def save_cmd_step_iter(self):
        self._dd += 1
        if self._dd >= self._dis:
            self.save_history_iter()        

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
