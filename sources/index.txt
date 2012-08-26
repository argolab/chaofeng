.. cháofēng documentation master file, created by
   sphinx-quickstart on Sun Aug 26 06:57:02 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to cháofēng's documentation!
====================================

cháofēng是一个简单的python telnet软件框架，主要用于开发bbs软件。

这份文档目前仅包括 :ref:`quickstart` 。API文档会在以后添加。

Code talks! 下面是一个简单的例子。服务器将会向客户端输出一句Hello, World::

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

cháofēng使用 `eventlet <http://eventlet.net/>`_ 进行了底层的封装。

Contents
========

.. toctree::
   :maxdepth: 1

   installation
   quickstart
   tutorial/index

待我英语写作能力提供，再来添加API接口文档 >w<

Contribute
==========

目前项目人手奇缺，欢迎加入～～不过你需要先想好你要干什么 囧rz...
`pull request <https://github.com/argolab/chaofeng/pulls>`_
是个非常不错的方法。

发现bug请使用github的 `issues <https://github.com/argolab/chaofeng/issues>`_
虽然其实我不大会用……

如果你有兴趣用chaofeng来写一个项目，欢迎跟我联系～虽然完全不需要～～

License
=======

License应该是GPLv3，因为名字很酷而且是最新版本……

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
