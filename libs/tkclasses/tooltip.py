
import Pmw

def new(widget, text):
    tt = Pmw.Balloon()
    tt.bind(widget, text)