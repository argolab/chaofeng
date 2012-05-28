from baseui import BaseUI
import chaofeng.ascii as ac

class ColMenu(BaseUI):

    key_maps = {
        ac.k_down : "move_down",
        ac.k_up : "move_up",
        ac.k_left : "move_left",
        ac.k_right : "move_right",
        }

    def __init__(self,data=None,height=None):
        self.shortcuts = {}
        self.pos = []
        self.values = []
        if data is not None:
            self.setup(data,height)

    def setup(self,data,height=None,background=''): 
        buf = [background]
        x = y = 0
        for index,item in enumerate(data) :
            if len(item) == 4 :
                text,value,key,(x,y) = item
                if not height : height = index
            else :
                text,value,key = item
                x += 1
            buf.append(ac.move2(x,y+2)+text)
            self.shortcuts[key] = index
            self.pos.append((x,y))
            self.values.append(value)
        self.len = len(data)
        self.height = height
        self.content = ''.join(buf)

    def init(self,default=0,refresh=True):
        self.hover = default
        if refresh : self.refresh()
        
    def fetch(self):
        return self.values[self.hover]

    def refresh(self):
        self.frame.write(self.content)
        self.frame.write(ac.move2(*self.pos[self.hover])+'>')

    def refresh_cursor(self):
        self.frame.write(ac.backspace+' '+ac.move2(*self.pos[self.hover])+'>')

    def send(self,data):
        if data in self.key_maps and hasattr(self,self.key_maps[data]) :
            getattr(self,self.key_maps[data])()
        if data in self.shortcuts :
            self.move_to(self.shortcuts[data])

    def move_down(self):
        if self.hover + 1 < self.len :
            self.hover += 1
        self.refresh_cursor()

    def move_up(self):
        if self.hover > 0 :
            self.hover -= 1
        self.refresh_cursor()

    def move_left(self):
        if self.height :
            next_s = self.hover - self.height
            if next_s >= 0 :
                self.hover = next_s
            self.refresh_cursor()

    def move_right(self):
        if self.height :
            next_s = self.hover + self.height
            if next_s < self.len :
                self.hover = next_s
            self.refresh_cursor()

    def move_to(self,which):
        self.hover = which
        self.refresh_cursor()
