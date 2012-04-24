from chaofeng.ascii import *
from string import Template

STATIC_PATH = './static/'

file_maps = {}

def file_map(suf):
    def fun_inner(frame):
        global file_maps
        file_maps[suf] = frame
        return frame
    return fun_inner

@file_map('.tpl')
def load_templete(f):
    la = f.readlines()
    if '----\n' in la : la = la[la.index('----\n')+1:]
    txt = u'\r'.join(la)[:-1]
    return Template(move2(0,0)+clear+txt)

import re

@file_map('.ani')
def load_animation(f):
    buf = []
    v = []
    for line in f :
        if line.startswith('----') :
            num = int(re.match('---- ([0-9]*)',line).group(1))
            v.append(('\r'.join(buf),num))
            buf = []
        else :
            buf.append(line)
    return v

def load_static():
    from os import walk
    from os import path as os_path
    import codecs
    '''Load the file under static path as string.'''
    path=STATIC_PATH
    v = {}
    global file_maps
    for root,dirs,files in walk(path):
        for filename in files :
            (name,suf) = os_path.splitext(filename)
            if suf in file_maps:
                with codecs.open(path+filename,'r',encoding="utf8") as f : 
                    v[name]=file_maps[suf](f)
    return v

static = load_static()

marks = {}

def mark(name):
    def mark_inner(frame):
        global marks
        marks[name] = frame
        return frame
    return mark_inner

import config

def _(s):
    return s.encode('gbk')
