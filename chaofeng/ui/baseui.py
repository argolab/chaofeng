
__metaclass__ = type

from copy import copy

class BaseUI:

    def init(self):
        raise NotImplementedError

    def new(self,frame):
        res = copy(self)
        res.frame = frame
        return res

    def copy(self):
        return copy(self)

    def send(self,data):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def clear(self):
        pass
