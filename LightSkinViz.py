#!/usr/bin/python3

import tkinter as tk
from typing import List

import math

from LightSkin import LightSkin


class LightSkinTopView(tk.Canvas):
    _LEDColor = '#444'
    _LEDColorS = '#5da'
    _SensorColor = '#955'
    _SensorColorS = '#fa8'
    _elRadius = 50
    _elScale = 100
    _border = 100

    def __init__(self, parent, skin: LightSkin, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.skin = skin
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.update()

        self._draw()
        skin.onChange += lambda *a, **kwa: self.updateVisuals()  # remove any parameters

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        # self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, wscale, hscale)

    def on_click(self, event):
        el = self.find_closest(event.x, event.y)[0]
        try:
            i = self._sensors.index(el)
            self.skin.selectedSensor = i
        except ValueError:
            try:
                i = self._leds.index(el)
                self.skin.selectedLED = i
            except ValueError:
                print("Nothing found")
                pass

    def updateVisuals(self):
        for i, o in enumerate(self._sensors):
            c = self._SensorColor
            if i == self.skin.selectedSensor:
                c = self._SensorColorS
            self.itemconfigure(o, fill=c)
        for i, o in enumerate(self._leds):
            c = self._LEDColor
            if i == self.skin.selectedLED:
                c = self._LEDColorS
            self.itemconfigure(o, fill=c)
        self.update()

    def _draw(self):
        self.delete("all")

        min_pos_x = None
        min_pos_y = None
        max_pos_x = None
        max_pos_y = None

        self._leds = []
        self._sensors = []
        for _s in self.skin.sensors:
            s = (_s[0] * self._elScale, _s[1] * self._elScale)
            o = self.create_rectangle(s[0] - self._elRadius, s[1] - self._elRadius, s[0] + self._elRadius,
                                      s[1] + self._elRadius, fill=self._SensorColor, width=0)
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

        for _s in self.skin.LEDs:
            s = (_s[0] * self._elScale, _s[1] * self._elScale)
            o = self.create_oval(s[0] - self._elRadius, s[1] - self._elRadius, s[0] + self._elRadius,
                                 s[1] + self._elRadius, fill=self._LEDColor, width=0)
            self._leds.append(o)
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

        wscale = self.width / float(max_pos_x - min_pos_x + 2 * self._border)
        hscale = self.height / float(max_pos_y - min_pos_y + 2 * self._border)
        scale = min(wscale, hscale)
        self.scale("all", 0, 0, scale, scale)

        self.tag_bind("all", '<ButtonPress-1>', self.on_click)
        pass


class LightSkinGridView(tk.Frame):
    _Color = '#eee'
    _LEDColorS = '#5da'
    _SensorColorS = '#fa8'
    _elRadius = 50
    _elScale = 100
    _border = 100

    def __init__(self, parent, skin: LightSkin, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.skin = skin

        self._build()
        skin.onChange += lambda *a, **kwa: self.updateVisuals()  # remove any parameters
        self.updateVisuals()

    def on_click(self, event):
        pass

    def updateVisuals(self):
        for i, b in enumerate(self._sensors):
            c = self._Color
            if i == self.skin.selectedSensor:
                c = self._SensorColorS
            b.configure(bg=c)
        for i, b in enumerate(self._leds):
            c = self._Color
            if i == self.skin.selectedLED:
                c = self._LEDColorS
            b.configure(bg=c)
        for i, l in enumerate(self._measurements):
            for j, f in enumerate(l):
                c = self._Color
                if i == self.skin.selectedLED:
                    c = self._LEDColorS
                if j == self.skin.selectedSensor:
                    c = self._SensorColorS
                val = self.skin.forwardModel.getSensorValue(j, i)
                v = int(math.sqrt(val) * 255)
                valcol = "#%02x%02x%02x" % (v, v, v)
                f.configure(highlightbackground=c, bg=valcol)
        pass

    def _build(self):
        self._sensors: List[tk.Button] = []
        self._leds: List[tk.Button] = []
        self._measurements: List[List[tk.Frame]] = []

        for i, s in enumerate(self.skin.sensors):
            def cmd(i=i):
                self.skin.selectedSensor = i

            b = tk.Button(self, text="S%i" % i, bg=self._Color, command=cmd)
            b.grid(column=0, row=i + 1)
            self._sensors.append(b)
        for i, s in enumerate(self.skin.LEDs):
            def cmd(i=i):
                self.skin.selectedLED = i

            b = tk.Button(self, text="L%i" % i, bg=self._Color, command=cmd)
            b.grid(column=i + 1, row=0)
            self._leds.append(b)

        for i in range(len(self.skin.LEDs)):
            self._measurements.append([])
            for j in range(len(self.skin.sensors)):
                f = tk.Frame(self, bg='#fff', highlightbackground=self._Color, highlightthickness=1)
                f.grid(column=i + 1, row=j + 1, sticky='NESW')
                self._measurements[i].append(f)

        pass
