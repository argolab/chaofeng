#!/usr/bin/python2
# -*- coding: utf-8 -*-
from chaofeng import Frame, Server
import chaofeng.ascii as ac
from chaofeng.ui import RadioButton

class ColorFrame(Frame):

    charset = 'gbk'

    def display_li(self, index, data):
        return '%s %-20s' % (chr(index+65), data)
        
    def initialize(self):
        op = {
            "Fuck":True,
            "ZOO":False,
            "DDE":True,
            }
        d = self.load(RadioButton, op, self.display_li)
        print d.read()

if __name__ == '__main__' :
    s = Server(ColorFrame)
    s.run()
