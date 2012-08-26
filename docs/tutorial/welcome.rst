.. _welcome:

第3步：登录画面
===============

好了，我们的登录画面！

::

    @mark('welcome')
    class IndexFrame(BaseFrame):

        def initialize(self):
            self.write(''.join([ac.clear, ac.move2(22,1)]))
            self.session.charset = 'utf8'
            while True:
                username_inputer = self.load(EastAsiaTextInput)
                username = username_inputer.readln(prompt=u'请输入你的用户名，没有则会注册一个：')
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

    if __name__ == '__main__' :
        s = Server(IndexFrame)
        s.run()

马上试一下！看看登录功能正常没有！
