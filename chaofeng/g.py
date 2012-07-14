__metaclass__ = type

from chaofeng.ascii import *
import os.path

import codecs,traceback

class Proxyer(dict):
    '''
    Dict callable , using to as decoration.
    '''
    def __call__(self,name):
        def mark_inner(obj):
            self[name] = obj
            obj.__mark__ = name
            return obj
        return mark_inner

# global dict of frame
mark = Proxyer()
