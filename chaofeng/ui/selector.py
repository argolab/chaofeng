from baseui import BaseUI
import chaofeng.ascii as ac

class ColMenu(BaseUI):

    key_maps = {
        ac.k_down : "move_down",
        ac.k_up : "move_up",
        ac.k_left : "move_left",
        ac.k_right : "move_right",
        }

    def init(self):
        self.shortcuts = {}
        self.pos = []
        self.values = []
        self.height = None

    def setup(self,data=None,height=None,background=None,hover=None):
        if hover is not None:
            self.hover = hover
        if background is not None:
            self.background = background
        if height is not None:
            self.height = height
        if data is not None:
            self.set_data(*data)

    def set_data(self,values,pos,shortcuts,outlook):
        self.values = values
        self.pos = pos
        self.shortcuts = shortcuts
        self.content = self.background + outlook
        self.len = len(self.values)

    def set_content(self,content):
        self.content = content

    @staticmethod
    def tidy_data(data):
        shortcuts = {}
        pos = []
        values = []
        buf = []
        for index,item in enumerate(data) :
            if len(item) == 4 :
                text,value,key,(x,y) = item
            else :
                text,value,key = item
                x += 1
            buf.append(ac.move2(x,y+2)+text)
            shortcuts[key] = index
            pos.append((x,y))
            values.append(value)
        return (values,pos,shortcuts,''.join(buf))

    def init(self,**kwargs):
        self.setup(**kwargs)
        
    def fetch(self):
        return self.values[self.hover]

    def restore(self):
        self.frame.write(self.content)
        self.frame.write(ac.move2(*self.pos[self.hover])+'>')

    def refresh_cursor(self):
        self.frame.write(ac.backspace+' '+ac.move2(*self.pos[self.hover])+'>')

    def send_shortcuts(self,data):
        if data in self.shortcuts :
            self.move_to(self.shortcuts[data])

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
                return True

    def move_right(self):
        if self.height :
            next_s = self.hover + self.height
            if next_s < self.len :
                self.hover = next_s
                self.refresh_cursor()
                return True

    def move_to(self,which):
        self.hover = which
        self.refresh_cursor()
