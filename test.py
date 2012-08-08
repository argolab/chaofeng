#!/usr/bin/python2
# -*- coding: utf-8 -*-
from chaofeng import Frame, Server
import chaofeng.ascii as ac
from chaofeng.ui import TextEditor, TextEditorAreaMixIn

class MyEditor(TextEditor, TextEditorAreaMixIn):
    pass

class ColorFrame(Frame):

    hotkeys = {
        ac.k_left:"move_left",
        ac.k_right:"move_right",
        ac.k_up:"move_up",
        ac.k_down:"move_down",
        ac.k_delete:"delete",
        ac.k_backspace:"backspace",
        ac.k_ctrl_l:"restore_screen",
        ac.k_enter_linux:"new_line",
        ac.k_ctrl_k:"kill_to_end",
        ac.k_ctrl_a:"move_beginning_of_line",
        ac.k_home:"move_beginning_of_line",
        ac.k_ctrl_e:"move_end_of_line",
        ac.k_end:"move_end_of_line",
        ac.k_ctrl_s:"goto_beginning_of_file",
        ac.k_ctrl_t:"goto_end_of_file",
        ac.k_ctrl_x:"exchange_pos",
        ac.esc:"insert_style",
        }

    second_hotkeys = {
        " ":"set_mark",
        ac.k_ctrl_u:"exchange_pos",
        ac.k_ctrl_d:"remove_area",
        }

    def initialize(self):
        self.editor = self.load(MyEditor,
                                u'世界，你好!\r\n'
                                u'Where Are 你\r\n'
                                u'1\r\n'
                                u'1\r\n')
        self.editor.restore_screen()

    def get(self, char):
        # print repr(char)
        if char in self.hotkeys:
            getattr(self.editor, self.hotkeys[char])()
        if char == ac.k_ctrl_u :
            char2 = self.read_secret()
            print ('alert', char2)
            if char in self.second_hotkeys:
                getattr(self.editor, self.second_hotkeys[char2])()
        if ac.is_safe_char(char):
            self.editor.insert_char(char)

if __name__ == '__main__' :
    s = Server(ColorFrame)
    s.run()
