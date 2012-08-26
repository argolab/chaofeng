.. _base:

第2步：公共基类
===============

考虑到我们会有比较多的输入输出和暂停，将这些写成一个公共的抽象类或许是个不错的方法。

::

    # -*- coding: utf-8 -*-

    from chaofeng import Frame, Server
    from chaofeng.g import mark
    from chaofeng.ui import EastAsiaTextInput, Password
    import chaofeng.ascii as ac

    MSG_BOX = {}
    USER_POOL = {}
    MAX_REGISTER = 200000

    class BaseFrame(Frame):

        pause_prompt = '%s%s%s%s' % (ac.move2(24,20), ac.outlook(ac.art_code['yellow'],
                                                                 ac.art_code['blink']),
                                     u'任意键继续', ac.reset)

        def wrong(self, msg):
            self.writeln(u'%s%s%s' % (ac.red, msg, ac.reset))

        def warning(self, msg):
            self.writeln(u'%s%s%s' % (ac.yellow, msg, ac.reset))

        def success(self, msg):
            self.writeln(u'%s%s%s' % (ac.green, msg, ac.reset))

        def pause(self):
            super(BaseFrame, self).pause(prompt=self.pause_prompt)
