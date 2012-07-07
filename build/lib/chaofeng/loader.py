#!/usr/bin/python2
from string import Template
from chaofeng.ascii import *
import re

def load_sequence(f):
    return [ x[:-1] for x in f.readlines()]

def load_text(f):
    return u'\r\n'.join(f.read().splitlines())

def load_templete(f):
    la = f.readlines()
    if '----\n' in la : la = la[la.index('----\n')+1:]
    txt = u'\r'.join(la)[:-1]
    return Template(move2(0,0)+clear+txt)

def load_animation(f):
    buf = []
    v = []
    for line in f :
        if line.startswith('----') :
            d = re.match('---- ([0-9]*)',line).group(1)
            d = int(d)
            v.append(('\r'.join(buf),d))
            buf = []
        else :
            buf.append(line)
    return v
