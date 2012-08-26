.. _main_menu:

第4步：主菜单
=============

好了，主菜单出场了！我们将会用到充满魔力的 ColMenu 模块！

::

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

这里用到了ColMenu，注意他的setup的第一个参数包括了四个list：

1. 第一个list表示该菜单项实际的值
2. 第二个表示该菜单项实际的屏幕位置
3. 第三个表示快捷键设置。其中key是快捷键，value是对应的菜单项的下标
4. 第四个是显示在屏幕上对应的文字

在 ``setup`` 以后，调用 ``restore`` 使其显示在屏幕上。

而get则检查是否为 ks_finish （一般即是回车），如果是，则取出 ``menu`` 的状态，
其返回值必定属于上面的第一个参数的第一个list的值。然后使用goto跳转到相应的frame。

如果不是，则尝试通过 ``send`` 发送给 菜单，让菜单自己响应。

