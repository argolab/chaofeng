.. _message:

第5步：留言和查看留言
=====================

重写UI模块的方法
----------------

留言可以使用 ``TextEditor`` 组件提供编辑画面，阅读留言则可以通过 ``SimpleTextBox``
查看。

``SimpleTextBox`` 将会使用整个屏幕，并且最后一行为底栏，用于显示信息。
要使用 ``SimpleTextBox`` ，继承它并重写他的 ``message`` 和 ``fix_bottom`` 方法。
这两个方法定义了阅读器的底栏的行为。

调用 ``SimpleTextBox`` 时只需要把要显示的内容和阅读结束时的回调函数传给它。
当用户按上，从阅读器的上方结束，将会调用 ``finish(True)`` ，下方结束则会调用
``finish(False)`` 。

查看留言
--------

::

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

编辑留言
--------

::

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

