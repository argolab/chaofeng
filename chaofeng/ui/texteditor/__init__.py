from baseui import BaseUI
import chaofeng.ascii as ac
from copy import deepcopy
from editor import TextBuffer
from editormod import *

class TextEditor(BaseUI,TextBuffer,
                       TextEditor_Cursor,TextEditor_Edit,
                       TextEditor_Mark,TextEditor_History):

    def __init__(self,**kwargs):
        self.__initmodules__(**kwargs)

    def init(self,**kwargs):
        self.action_hook("__init__")

    def refresh_iter(self):
        self.refresh_all()

    def message(self,msg):
        print msg

__all__ ["TextEditor"]
