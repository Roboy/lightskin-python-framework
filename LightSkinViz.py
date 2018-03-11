#!/usr/bin/python3

import tkinter as tk


class LightSkinTopView(tk.Canvas):
    skin = None

    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def draw(self):
        pass
