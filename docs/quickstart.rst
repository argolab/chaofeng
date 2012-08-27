.. _quickstart:

快速上手 
=========

好了，我们要准备开始了。不过在开始以前，确认你已经装好了 Chaofeng ，
否则请先阅读 :ref:`installation` 。[#hello-eg]_

::

    from chaofeng import Frame, Server
    
    class HelloFrame(Frame):
    
        def initialize(self):
            self.write(u'Hello,World!\r\n')
            self.pause()
            self.close()

    if __name__ == '__main__' :
        s = Server(HelloFrame)
        s.run()


把他保存为 `hello.py` 然后用你的python解释器运行这个文件。

::

    $ python hello.py
    RUNNING -- Sun Aug 26 08:55:54 2012

然后，开启你的终端机或者仿真终端软件，然后telnet进入本机，比如::

    $ telnet localhost 5000

然后就会看到你的问候了。

这段代码神马意思呢？

1. 我们导入了 ``Frame`` , ``Server`` 类。
2. 构造了一个 ``Frame`` 的派生类 ``HelloFrame`` ，重写了他的 ``initialize`` 方法。
3. ``initialize`` 方法表明，向客户端发送 ``Hello,World!`` ，
   换行然后等到一个按键，最后关闭连接。
4. 将 ``HelloFrame`` 类作为第一个参数传给了 ``Server`` ，实例化一个 ``Server`` 类。
5. 让 ``Server`` 跑起来！

按 control-C 可以停止服务器。

.. [#hello-eg] 这个例子是抄袭 `flask <http://flask.pocoo.org/docs/quickstart/#a-minimal-application>`_ 的。 

.. _class-frame:

``Frame`` : 盒子
----------------

chaofeng的设定中，一个应用是由许多Frame构成的。一个Frame对应于一个使用的场景，
定义了如何和用户交互。每个连接在任何时候都属于且只属于一个Frame。

你需要重写Frame类的几个方法，来让这个Frame工作。一般地，你需要重写
``initialize`` ，当一个连接进入这个Frame的时候，就会调用这个方法。
如果有需要，可以重写 ``clear`` 方法，当用户离开的时候，就会调用这个方法。

通过 ``write`` 方法向客户端发送内容。另外，你可以通过 ``read`` 和
``read_secret`` 方法来获得用户的输入。 ``read``会等待用户的输入，
并将输入的结果返回（参见 :ref:`ascii` ），同时，
这个字符会被发送到到Frame的 ``get`` 函数执行。而 ``read_secret`` 类似，
但不会发送到 ``get`` 函数。

如果一个Frame没有被关闭（调用 ``close`` 方法），在 ``initialize`` 结束后，
将会进入一个不断read的死循环。事实上，大多数情况只需要重写 ``get``
方法而不用显示地调用 ``read`` 和 ``read_secret`` 。

这有什么意义呢？在telnet软件中，大部份的行为都是 ``读取-动作执行`` 的形式，
你可以把一个frame的 ``读取-动作执行`` 集中地放在 ``get`` 函数这个统一的接口中。

下面是一个简单的例子::

    from chaofeng import Frame, Server

    action = {
        "n":"print_314",
        "h":"print_hello",
        }
    
    class HelloFrame(Frame):
    
        def initialize(self):
            self.print_hello()
            
        def get(self, char):
            if char in action :
                getattr(self, action[char])()

        def print_314(self):
            self.write(u'3.14\r\n')

        def print_hello(self):
            self.write(u'Hello,World!\r\n')

    if __name__ == '__main__' :
        s = Server(HelloFrame)
        s.run()
    
原谅我使用这个无聊的例子。这个例子的亮点在于 ``get`` 函数。
我们检查用户的输入是不是在 ``action``  字典中，如果是，就调用相应的方法。

然后， ``Server`` 类就没什么好玩的了。他会将每个连接自动进入传给他的那个参数。
然后，你可以通过传入 ``port`` 关键字参数给他，设定要绑定的端口，
这个端口默认是 ``5000`` ，而一般telnet使用 ``23`` ::

    s = Server(YourFrame, port=23)
    s.run()

哈哈！你一定期望我实现了一个debug模式，然后传入debug关键字参数。
遗憾的是我并没有实现……

.. _goto-mark:

``mark`` , ``goto`` :在盒子间飞舞
---------------------------------

在介绍 ``goto`` 以前，请让我先介绍他的父亲 ``raw_goto`` 。把全部的
活动放在一个frame是可行的，但可能不是最好的方案。我们通过写多个frame，
并在这些frame中切换，实现模块化。没错，这就是 ``raw_goto`` 和 ``goto``
要干的事::

    from chaofeng import Frame, Server

    class Frame1(Frame):

        def initialize(self):
            self.write(u'I am frame1 XD \r\n')
            self.pause()
            self.raw_goto(Frame2)

    class Frame2(Frame):

        def initialize(self):
            self.write(u"I am frame1's brother >3< \r\n")
            self.pause()
            self.close()

    s = Server(Frame1)
    s.run()

或许你可以猜测一下会发生什么？

1. 首先进入了 ``Frame1``
2. 你得到了一句 ``Frame1`` 的自我介绍
3. 你按下了一个键，然后被 ``Frame1`` 推给了他的哥哥 ``Frame2``
4. ``Frame2`` 告诉你他是 ``Frame1`` 的哥哥。
5. 你按下了一个键，然后连接关闭了。

注意到 ``raw_goto`` 以后的语句，在本个 ``Frame`` 中的函数将不会被执行::

    raw_goto(AnotherFrame)
    this_will_never_execute()

因为你已经跳出这个Frame了！

好了，下面我们来介绍 ``mark`` 叔叔和 ``goto`` 叔叔。你需要这样使用他们::

    from chaofeng import Frame,Server
    from chaofeng.g import mark

    @mark('frame_one')
    class Frame1(Frame):

        def xxxoo(self):
            self.goto('frame_two')

    @mark('frame_two')
    class Frame2(Frame):
        do_something()
        #....

甜蜜蜜的语法糖！一般地，倾向于使用 ``mark`` 和 ``goto`` ，而 ``mark``
可以使用任意的字符串名来作为标记。而且装饰器看起来比较酷。

为什么不可以在 ``goto`` 的时候带点参数呢？是的，这是可以的::

    # +r -w -x

    @mark('say_hello')
    class HelloFrame2(Frame):

        def initialize(self, name):
            self.write('Hello, %s!' % name)

    class Frame2(Frame):

        def initialize(self):
            self.pause()
            self.goto('say_hello', 'World')

.. _session:

``session`` : 副作用也不错
--------------------------

不知道你有没有发现，还有一点小问题。比如，我们需要为每个session保存一个用户名，
我们居然发现我们没有办法在 ``goto`` 以后保存。恩，我们需要一点类似于web cookie的东西，
它可以保存我们在 ``goto`` 的时候依然需要保留的某些东西。

对，我们可以把这些要保存的东西在 ``goto`` 的时候作为参数传来传去。但是有时候有点
side effect也是可以的。我们有 ``session`` 。他是一个字典。
而且每个连接的session在 ``goto`` 的时候, 对这个连接来说， ``session`` 总是同一东西::

    # +r -w -x

    @mark('get_username')
    class GetUserNameFrame(Frame):

        def initialize(self):
            self.session['username'] = 'World'
            self.goto('say_hello')

    @mark('say_hello')
    class SayHelloFrame(Frame):

        def initizlize(self):
            self.write(u'Hello, %s' % self.session['username'])
            self.pause()
            self.close()

再次原谅我又使用了一个无聊的例子，但相信你可以由此明白 ``session`` 的作用了。

如果你对 ``self.session`` 是一个字典不满足，可以期待下次他有个华丽的变身。

.. _ascii:

``ascii`` :来自ASCII的魔法
--------------------------

telnet使用的交互方式异常简单。telnet只支持8种颜色（ANSI-Term)。
而这些颜色都是由特殊的控制码来控制的。一般的命令行程序的库都会用一个更超级的封装层包装，
以消除不同的term直接的差异。但chaofeng没有。chaofeng没有准备支持全部的term。事实上，
大多数的term的实现都是 ANSI Term 的实现（vt100)。而且现在使用奇怪的term并不常见了，
多数是使用终端机仿真机来使用telnet，也即是多数是vt100的。

考虑这样的一个字符串::

    \x1b[31m红色字符\x1b[m

其中的\x1b表示 ESC ，是一个不可见的字符。上面这个字符串在vt100终端机中（现代多数都是），
就会显示一个红色的 ``红色字符`` 。

chaofeng收集了一些常见的这些字符串，直接作为字符串或者函数收录在 ``chaofeng.ascii`` 模块中。
你可以像这样使用：

::

    import chaofeng.ascii as ac

    #...
    self.write(u'%sRed Char%s' % (ac.red, ac.reset))
    #...

一些常用的字符串和函数，和一些例子列在下面

* reset
* black, red, green, yellow, blue, magenta, cyan  # 字体色
* bg_black, bg_red, ...   # 背景色
* bold, underscore, inverted, italic, blink
* outlook(art_code['black'], art_code['bg_green'])
* move2(24, 1)  # 移动光标的位置到24,1
* save # 保存光标位置
* restore  # 恢复光标位置
* clear  # 清除屏幕
* insert1 # 插入一个空行
* kill_to_end # 删除至行尾

另外，考虑我们按下了一系列的按键，比如我们输入了 ``SHIFT+h``  ``x``  ``BACKSPACE``  ``e``
这里的BACKSPACE表示退格键。那么，实际上我们调用 ``frame.read`` 方法四次会得到 ``H`` ``x``
``\x7f``  ``e`` 。也就是，所有的按键都有一个实际的字符串与之对应。对此，
chaofeng也提供了一些简单的包装::

    char = self.read_secret()
    if char == ac.k_delete :
        self.write(u'You press the DELETE')

是的，我相信你看懂了。这些按键表示的字符串也全部包括在ascii模块中，而且全部的按键序列都以
``k_`` 为前缀。一些常用的列举如下：

* k_up, k_down, k_left, k_right  # 光标键
* k_ctrl_{k}   # CTRL+{k} 其中{k}是一个小写字母
* k_home, k_end, k_page_up, k_page_down
* ks_enter # 这是一个set！用 char in ks_enter 判断

.. _uimodule:

``ui`` 模块 :重用吧！古老的交互
--------------------------------

恩，有点杯具，现在我们都不知道如何输入一个用户名（注意到 ``read`` 只能读一个字符）。

这个其实是古老的telnet所设定的。因为telnet协议本身并没有对输入和用户交互有太多定义。
事实上， ``输入`` 的实现是由服务器自己实现的，也即是需要手工模拟。

chaofeng逐渐提供了一些这方面的组件。我们把更用户交互相关的，
或者重用率高的东西包装为一个 UI组件 。然后你可以来使用他们。下面是一个简单的例子::

    from chaofeng import Frame, Server
    from chaofeng.ui import VisableInput

    class HelloFrame(Frame):

        def initialize(self):
            inputer = self.load(VisableInput, buffer_size=20)
            username = inputer.read(prompt=u'Please input you username:')
            self.write(u'Hello, %s' % username)

恩，应该很好懂:

1. 从 ``chaofeng.ui`` 导入 ``VisableInput`` 组件
2. 在 ``HelloFrame`` 的 ``initialize`` 方法中加载( ``self.load`` )这个组件，
   将返回值绑定为 ``inputer`` 。其中，这个组件的buffer最多接受 ``20`` 个字符。
3. 让 ``inputer`` 来读，将读取的结果返回给 ``username``
4. 输出 ``username`` 。

你可以试一下！是可以支持按 DEL 键来删除不想要的字符的！

类似的，我们还有许多的 UI组件 ：

* 输入： BaseInput, VisableInput, EastAsiaTextInput, Password, DatePicker
* ColMenu： 列菜单
* Form : 多个输入的交互处理
* Animation : ascii动画
* LongTextBox ： 长文本阅读器
* ListBox : 列表容器
* PagedTable：表格
* TextEditor：编辑器

可能你会发现，这些组件都是直接从现在的telnet bbs上面抽象出来的。

.. _charset:

``charset`` :字符编码
---------------------

所有数据在内部都应该使用unicode的。 ``write`` 和 ``read`` 方法会去查询
``self.session.charset`` 的值，将字符流解码为unicode然后在内部表示，输出时则编码为相应的字符流。

特别的， ``read`` 和 ``read_secret`` 都会将收到的资料分解为单个字符（语义上为单个，比如 ``ac.k_up``)
不需要 ``for char in self.read()`` 这种形式的语句，因为 ``self.read()`` 的值语义上总是为单个的字符。

不同的session使用不同的字符编码是可以的，只需要设置好相应的 ``self.session.charset`` 即可。同时，
应该保证 ``self.write`` 的参数必须是 unicode 。但chaofeng不会检查，write其他类型的后果是未定义的。

解码的函数为 ``self.u`` ，这个函数会将传入的字符串，根据 ``self.session.charset`` 解码为unidoe，
而编码的则是 ``self.s`` 。

好了，快速上手到这里结束了，如果你还有兴趣，不妨继续阅读 :ref:`tutorial` 。
