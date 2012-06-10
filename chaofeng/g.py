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

class StaticProxyer:

    '''
    Load the static resouce.
    '''

    def __init__(self,**kwargs):
        self.loader = {}
        self.dict = {}
        self.config(**kwargs)
        
    def config(self,root=None,loader=None,encoding="utf8"):
        if root :
            self.root = os.path.normpath(root)
        if loader : 
            self.loader.update(loader)
        if encoding :
            self.encoding=encoding
        
    def _load(self,key):
        for suf in self.loader :
            fpath = os.path.join(self.root,key + suf)
            if os.path.exists(fpath) :
                with codecs.open(fpath,encoding=self.encoding) as f:
                    self.dict[key] = self.loader[suf](f)
                    return self.dict[key]
        raise ValueError,"No available file for %s" % key

    def __getitem__(self,key):
        return self.dict.get(key) or self._load(key)

import default_config

setting = default_config.static

static = StaticProxyer(**setting)
