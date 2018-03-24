from tkinter import *


# Adapted from http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
class ToolTip(object):
    distance = 20

    def __init__(self, widget, text=None):
        self._text = text
        self.widget = widget
        self.tipwindow = None
        self.label: Label = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text=None):
        "Display text in tooltip window"
        if text is not None:
            self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.distance
        y = y + cy + self.widget.winfo_rooty() + self.distance
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass
        self.label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        self.label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.label = None
        self.tipwindow = None
        if tw:
            tw.destroy()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        if self.label is not None:
            self.label.configure(text=self.text)

    @staticmethod
    def createToolTip(widget: Widget, text):
        toolTip = ToolTip(widget, text)

        def enter(event):
            toolTip.showtip()

        def leave(event):
            toolTip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
        return toolTip
