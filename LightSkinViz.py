#!/usr/bin/python3

import tkinter as tk

from LightSkin import LightSkin


class LightSkinTopView(tk.Canvas):
    _LEDColor = '#444'
    _LEDColorS = '#5f7'
    _SensorColor = '#522'
    _SensorColorS = '#775'
    _border = 10

    skin: LightSkin = None

    def __init__(self, parent, skin: LightSkin, **kwargs):
        tk.Canvas.__init__(self, parent, highlightthickness=0, **kwargs)
        self.skin = skin
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.update()

        self._draw()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)



    def _draw(self):
        self.delete("all")

        min_pos_x = None
        min_pos_y = None
        max_pos_x = None
        max_pos_y = None

        self._leds = []
        self._sensors = []
        for s in self.skin.sensors:
            o = self.create_rectangle(s[0]-0.5, s[1]-0.5, s[0]+0.5, s[1]+0.5, fill=self._SensorColor)
            self._sensors.append(o)
            if min_pos_x is None:
                min_pos_x = s[0]
                min_pos_y = s[1]
                max_pos_x = s[0]
                max_pos_y = s[1]
            if min_pos_x > s[0]:
                min_pos_x = s[0]
            if min_pos_y > s[1]:
                min_pos_y = s[1]
            if max_pos_x < s[0]:
                max_pos_x = s[0]
            if max_pos_y < s[1]:
                max_pos_y = s[1]

        for s in self.skin.LEDs:
            o = self.create_oval(s[0]-0.5, s[1]-0.5, s[0]+0.5, s[1]+0.5, fill=self._SensorColor)
            self._sensors.append(o)
            if min_pos_x > s[0]:
                min_pos_x = s[0]
            if min_pos_y > s[1]:
                min_pos_y = s[1]
            if max_pos_x < s[0]:
                max_pos_x = s[0]
            if max_pos_y < s[1]:
                max_pos_y = s[1]


        # calculate scaling necessary to apply

        self.move("all", self._border - min_pos_x, self._border - min_pos_y)

        wscale = self.width /  float(max_pos_x - min_pos_x + 2*self._border)
        hscale = self.height / float(max_pos_y - min_pos_y + 2*self._border)
        self.scale("all", 0, 0, wscale, hscale)
        pass
