from tkinter import *


# Adapted from http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
# Which has been released as part of http://www.voidspace.org.uk/python/movpy/
# under the BSD-3 clause
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
        """Display text in tooltip window"""
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


# Copyright (c) 2006-2009, Michael Foord
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#         Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#         Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#         Neither the name of the Movable Python nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.