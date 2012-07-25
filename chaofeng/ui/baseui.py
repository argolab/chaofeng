__metaclass__ = type

from copy import copy

class BaseUI:

    def __init__(self, frame):
        self.frame = frame
        
    def init(self):
        raise NotImplementedError

    def fetch(self):
        raise NotImplementedError

    def clear(self):
        pass

    def do_command(self, action):
        if action:
            getattr(self, action)()
