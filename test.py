from chaofeng import Frame, Server
import chaofeng.ascii as ac
from chaofeng.ui import VisableInput,BaseInput,EastAsiaTextInput,Password,DatePicker

class ColorFrame(Frame):

    charset = 'gbk'

    def initialize(self):
        d = self.load(DatePicker)
        print repr(d.read(prompt='Hello: '))
                #acceptable=lambda x:True,
                          # buf=None,
                          # prompt='Hello!')
                          # termitor=ac.ks_finish))
        print d.fetch_str()        

if __name__ == '__main__' :
    s = Server(ColorFrame)
    s.run()
