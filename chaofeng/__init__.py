# -*- coding: utf-8 -*-
'''
    Cháofēng
    ~~~~~~~~

    A low-level telnet bbs server framework base on eventlet.  It's made up with love
    and respect.

    :copyright: (c) 2012 by Mo Norman
    :license: GPLv3

'''

__version__ = '0.09'

from eventlet import Timeout
from eventlet.greenthread import sleep
from eventlet import spawn_after as setTimeout
from eventlet import spawn as launch

import ascii
import ui
import g
from .bbs import Server,Frame,EndInterrupt,asynchronous
