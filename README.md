cháofēng
========

A low-level telnet bbs server framework base on [eventlet](http://eventlet.net/).
It's made up with love and respect.

更多的文档点[这里](http://argolab.github.com/chaofeng/)。

Hello,World!
------------

```python

    from chaofeng import Frame, Server

    class HelloFrame(Frame):

        def initialize(self):
            self.write('Hello,World!\r\n')
            self.pause()
            self.close()

    if __name__ == '__main__' :
        s = Server(HelloFrame)
        s.run()
```

Test it!
--------

```bash
git clone https://github.com/argolab/chaofeng.git
cd chaofeng
python test.py
```

In client:

```bash
telnet localhost 5000
```
