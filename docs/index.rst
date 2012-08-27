.. cháofēng documentation master file, created by
   sphinx-quickstart on Sun Aug 26 06:57:02 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to cháofēng's documentation!
====================================

cháofēng是一个简单的python telnet软件框架，主要用于开发bbs软件。

这份文档目前包括 :ref:`installation` 、 :ref:`quickstart` 和 :ref:`tutorial` 。
API文档会在以后添加。首先，阅读 :ref:`installation` 来安装。然后， :ref:`quickstart`
包括一个简单的说明，可以快速了解 chaofeng 的结构和提供的工具。最后如果你还有兴趣，
阅读 :ref:`tutorial` ，它完成了一个简单的bbs软件，

Code talks! 下面是一个简单的例子。服务器将会向客户端输出一句Hello, World::

    from chaofeng import Frame, Server
    
    class HelloFrame(Frame):
    
        def initialize(self):
            self.write('Hello,World!\r\n')
            self.pause()
            self.close()

    if __name__ == '__main__' :
        s = Server(HelloFrame)
        s.run()

cháofēng使用 `eventlet <http://eventlet.net/>`_ 进行了底层的封装，
是一个 非阻塞I/O 和多协程的服务器框架。但您并不需要了解eventlet。

Contents
========

.. toctree::
   :maxdepth: 1

   installation
   quickstart
   tutorial/index

待我英语写作能力提高，再来添加API接口文档 >w< 这之前，
或许你可以考虑阅读 `chaofeng in github`_ 。

.. _chaofeng in github:
   https://github.com/argolab/chaofeng    

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
