.. _testing:

第6步：测试,跑起来！
====================

最后，把这些全部拼起来，下面是一个完整的mmssgg。

.. code-block:: python
   :linenos:

    # -*- coding: utf-8 -*-

    from chaofeng import Frame, Server
    from chaofeng.g import mark
    from chaofeng.ui import EastAsiaTextInput, Password, ColMenu, SimpleTextBox,\
        TextEditor
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

        def warnning(self, msg):
            self.writeln(u'%s%s%s' % (ac.yellow, msg, ac.reset))

        def success(self, msg):
            self.writeln(u'%s%s%s' % (ac.green, msg, ac.reset))

        def pause(self):
            super(BaseFrame, self).pause(prompt=self.pause_prompt)

    ##############        

    @mark('welcome')
    class IndexFrame(BaseFrame):

        def initialize(self):
            self.write(''.join([ac.clear, ac.move2(22,1)]))
            self.session.charset = 'utf8'
            while True:
                username_inputer = self.load(EastAsiaTextInput)
                username = username_inputer.readln(prompt=u'请输入你的用户名，没有则会注册一个：')
                if not username :
                    continue
                password_inputer = self.load(Password)
                password = password_inputer.readln(prompt=u'请输入你的密码：')
                if username in USER_POOL :
                    if USER_POOL[username] != password :
                        self.wrong(u'用户名与密码不匹配！')
                        continue
                    self.success(u'登录成功！')
                else:
                    if len(USER_POOL) >= MAX_REGISTER:
                        self.wrong(u'对不起，已达最大注册人数！')
                        self.close()
                    self.success(u'注册新用户！')
                    USER_POOL[username] = password
                    MSG_BOX[username] = u'欢迎使用！您还没有留言！'
                break
            self.session['username'] = username
            self.pause()
            self.goto('main_menu')

    ##############        

    @mark('main_menu')
    class MainMenuFrame(BaseFrame):

        def initialize(self):
            self.write(''.join([
                        ac.clear,
                        ac.move2(10, 50),
                        ac.outlook(ac.art_code['red'], ac.art_code['bold']),
                        'M M S S G G',
                        ac.reset]))
            self.menu = self.load(ColMenu)  # 记住要先import ColMenu
            self.menu.setup([
                    ['show_message', 'set_message', 'delete_self', 'bye'],
                    [(8,20), (10,22), (12, 24), (14, 26)],
                    {'a':0, 'b':1, 'c':2, 'd': 3},
                    [u'a. 查看留言', u'b. 设置留言', u'c. 删除资料', u'd. 离开系统'],
                    ])
            self.menu.restore()

        def get(self, char):
            if char in ac.ks_finish:
                next_frame = self.menu.fetch()
                self.goto(next_frame)
            self.menu.send(char)

    ##############        

    @mark('bye')
    class GoodByeFrame(BaseFrame):

        def initialize(self):
            self.writeln(u'欢迎下次再来！')
            self.pause()
            self.close()

    ##############        

    @mark('delete_self')
    class DeleteSelfFrame(BaseFrame):

        def initialize(self):
            del USER_POOL[self.session['username']]
            del MSG_BOX[self.session['username']]
            self.success(u'\r\n%s删除资料成功！下面将自动离开系统！' % ac.move2(22, 1))
            self.pause()
            self.close()

    ##############        

    class MmssggTextBox(SimpleTextBox):

        def message(self, message):
            self.frame.write(''.join([ac.move2(24, 1), ac.kill_to_end,
                                      ac.outlook(ac.art_code['bg_blue'],
                                                 ac.art_code['yellow'],
                                                 ac.art_code['bold']),
                                      message, ac.reset]))

        def fix_bottom(self):
            self.message(u'')

    @mark('show_message')
    class ShowMessageFrame(BaseFrame):

        hotkeys = {
            ac.k_ctrl_l : "restore_screen",
            ac.k_up : "move_up",
            ac.k_down : "move_down",
            ac.k_home : "goto_first",
            ac.k_end : "goto_last",
            ac.k_page_up : "page_up",
            ac.k_page_down : "page_down",
            }

        def initialize(self):
            content = MSG_BOX[self.session['username']]
            self.textbox = self.load(MmssggTextBox, content, self.read_finish)
            self.textbox.restore_screen()

        def get(self, char):
            if char in self.hotkeys :
                getattr(self.textbox, self.hotkeys[char])()

        def read_finish(self, arg):
            self.goto('main_menu')

    ##############        

    class MmssggTextEditor(TextEditor):

        def bottom_bar(self, msg=u''):
            self.frame.write(''.join([ac.move2(24, 1), ac.kill_to_end,
                                      ac.outlook(ac.art_code['bg_blue'],
                                                 ac.art_code['yellow'],
                                                 ac.art_code['bold']),
                                      msg, ac.reset]))
            self.fix_cursor()

        def get(self, char):
            if char in ac.ks_finish:
                self.goto('main_menu')
            if char in self.hotkeys :
                getattr(self, self.hotkeys[char])()

        def do_command(self, cmd):
            getattr(self, cmd)()
            self.bottom_bar()

    @mark('set_message')
    class EditMessageFrame(BaseFrame):

        hotkeys = TextEditor.like_emacs_hotkeys

        def initialize(self):
            text = MSG_BOX[self.session['username']]
            self.editor = self.load(MmssggTextEditor, text, 0)
            self.editor.restore_screen()
            self.editor.fix_cursor()

        def get(self, char):
            if char in ac.k_ctrl_w:
                self.finish()
            if char in self.hotkeys :
                self.editor.do_command(self.hotkeys[char])
            elif ac.is_safe_char(char):
                self.editor.insert_char(char)

        def finish(self):
            text = self.editor.fetch_all()
            MSG_BOX[self.session['username']] = text
            self.editor.bottom_bar(u'修改留言成功！')
            self.pause()
            self.goto('main_menu')

    if __name__ == '__main__' :
        s = Server(IndexFrame)
        s.run()

然后，跑起来！

::

     $ python mmssgg.py

客户端：

::

     $ telnet localhost 5000

