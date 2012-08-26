# -*- coding: utf-8 -*-

'''
    A quick example for chaofeng.
    
'''

from chaofeng import Frame, Server
import chaofeng.ascii as c

class HelloFrame(Frame):

    def initialize(self):
        self.write('Hello,World!\r\n')
        self.pause()
        self.close()

if __name__ == '__main__' :
    s = Server(HelloFrame)
    s.run()
