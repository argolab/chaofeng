# -*- coding: utf-8 -*-
'''
    chaofeng.g
    ~~~~~~~~~~

    Some collections for global variables and setting.
'''

__metaclass__ = type

class Proxyer(dict):
    '''A dict that allows for setting item as decoration. '''
    def __call__(self,name):
        def mark_inner(obj):
            self[name] = obj
            obj.__mark__ = name
            return obj
        return mark_inner

# global dict of frame
mark = Proxyer()
