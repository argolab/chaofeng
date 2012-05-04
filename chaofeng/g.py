__metaclass__ = type

from chaofeng.ascii import *
from string import Template
from os import walk as os_walk
from os import path as os_path
import re
import codecs

class Proxyer(dict):
    '''
    Dict callable , using to as decoration.
    '''
    def __call__(self,name):
        def mark_inner(obj):
            self[name] = obj
            return obj
        return mark_inner

# global dict of frame
mark = Proxyer()

# Normal file map 
f_map = Proxyer()

@f_map('.seq')
def load_seq(f):
    return [ x[:-1] for x in f.readlines()]

@f_map('.txt')
def load_str(f):
    return u'\r'.join(f.readlines())[:-1]

@f_map('.tpl')
def load_templete(f):
    la = f.readlines()
    if '----\n' in la : la = la[la.index('----\n')+1:]
    txt = u'\r'.join(la)[:-1]
    return Template(move2(0,0)+clear+txt)

@f_map('.ani')
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

class StaticProxyer(Proxyer):
    '''
    Load the static resouce.
    '''
    def load(self,path='./static/',file_map=None,encoding="utf8",mode="r"):
        if file_map == None :
            file_map = f_map
        for root,dirs,files in os_walk(path):
            for filename in files :
                (name,suf) = os_path.splitext(filename)
                if suf in file_map:
                    with codecs.open(path+filename,mode,encoding=encoding) as f :
                        self[name]=file_map[suf](f)

static = StaticProxyer()
static.load()

_s = lambda s : s.encode('gbk') if isinstance(s,unicode) else s
_u = lambda s : s.decode('gbk')

def _d(format_str,obj):
    n_obj = dict( (key, obj[key].encode('gbk') if\
                       isinstance(obj[key],unicode) else obj[key] ) for key in obj )
    return ( format_str.encode('gbk') % n_obj).decode('gbk')

def _w(format_str,*obj):
    n_obj = tuple( i.encode('gbk') if isinstance(i,unicode) else i for i in obj )
    return ( format_str.encode('gbk') % n_obj ).decode('gbk')
