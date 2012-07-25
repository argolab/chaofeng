
from ..baseui import BaseUI
import chaofeng.ascii as ac
from copy import deepcopy
from editor import TextBuffer
from editormod import *
from datetime import datetime

class TextEditor(BaseUI,TextBuffer,
                       TextEditor_Cursor,TextEditor_Edit,
                       TextEditor_Mark,TextEditor_History):

    SCR_HEIGHT = 23
    
    bottom_text = ac.move2(SCR_HEIGHT+1,0) + ac.kill_line + 'chaofeng : [%d,%d] %s'

    def init(self,height=23,**kwargs):
        self.__initmodules__(height=height,**kwargs)
        self.reset()

    def reset(self):
        self.action_hook("__init__")

    def bottom_bar(self):
        l,r = self.getlr()
        self.write(self.bottom_text % (l,r,datetime.now().ctime()))
        self.fix_cursor()

    def char_width(self,char):
        return ac.srcwidth(char)

    def refresh_iter(self):
        self.refresh_all()

    def message(self,msg):
        print msg

    def write(self,data):
        self.frame.write(data)

    def safe_insert_iter(self,char):
        char = filter(ac.is_safe_char,self.frame.u(char))
        for c in char:
            self.insert_iter(c)

__all__ = ["TextEditor"]
