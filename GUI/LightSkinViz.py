#!/usr/bin/python3

import tkinter as tk
from typing import List, Callable, Tuple

import math

from Helpers.Measurable import MeasurableGrid
from LightSkin import LightSkin
from GUI.TKinterToolTip import ToolTip


class LightSkinTopView(tk.Canvas):
    _LEDColor = '#475'
    _LEDColorS = '#5da'
    _SensorColor = '#955'
    _SensorColorS = '#fa8'
    _elRadius = 50
    _elScale = 100
    _border = 100

    def __init__(self, parent,
                 skin: LightSkin,
                 gridWidth: int = None,
                 gridHeight: int = None,
                 measurable_grid: MeasurableGrid = None,
                 measure_function: Callable[[float, float], float] = lambda x, y: 0,
                 display_function: Callable[[float], float] = lambda x: x,
                 **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.measureFunction = measure_function
        self.displayFunction = display_function
        self.skin = skin

        if measurable_grid is not None:
            gdef = measurable_grid.getGridDefinition()
            self.gridWidth = gdef.cellsX
            self.gridHeight = gdef.cellsY
            self.measureFunction = measurable_grid.measureAtPoint

        if gridWidth is not None:
            self.gridWidth = gridWidth
        if gridHeight is not None:
            self.gridHeight = gridHeight

        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.update()

        self._draw()
        skin.onChange += lambda *a, **kwa: self.updateVisuals()  # remove any parameters
        self.updateVisuals()

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
                print("Click target not found")
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

        rect_w = float(self._max_pos_x - self._min_pos_x) / self.gridWidth
        rect_h = float(self._max_pos_y - self._min_pos_y) / self.gridHeight
        for i, c in enumerate(self._grid):
            for j, o in enumerate(c):
                x = (self._min_pos_x + (float(i)+0.5)*rect_w) / self._elScale
                y = (self._min_pos_y + (float(j)+0.5)*rect_h) / self._elScale
                #print('Measuring at %f, %f' % (x, y))
                val = self.measureFunction(x, y)
                v = int(self.displayFunction(val) * 255)
                valcol = "#%02x%02x%02x" % (v, v, v)
                self.itemconfigure(o, fill=valcol)

    def _draw(self):
        self.delete("all")

        self._min_pos_x: float = math.inf
        self._min_pos_y: float = math.inf
        self._max_pos_x: float = -math.inf
        self._max_pos_y: float = -math.inf

        self._leds = []
        self._sensors = []
        for _s in self.skin.sensors:
            s = (_s[0] * self._elScale, _s[1] * self._elScale)
            o = self.create_rectangle(s[0] - self._elRadius, s[1] - self._elRadius, s[0] + self._elRadius,
                                      s[1] + self._elRadius, fill=self._SensorColor, width=0, tags=['sensor'])
            self._sensors.append(o)
            self._min_pos_x = min(self._min_pos_x, s[0])
            self._max_pos_x = max(self._max_pos_x, s[0])
            self._min_pos_y = min(self._min_pos_y, s[1])
            self._max_pos_y = max(self._max_pos_y, s[1])

        for _s in self.skin.LEDs:
            s = (_s[0] * self._elScale, _s[1] * self._elScale)
            o = self.create_oval(s[0] - self._elRadius, s[1] - self._elRadius, s[0] + self._elRadius,
                                 s[1] + self._elRadius, fill=self._LEDColor, width=0, tags=['led'])
            self._leds.append(o)
            self._min_pos_x = min(self._min_pos_x, s[0])
            self._max_pos_x = max(self._max_pos_x, s[0])
            self._min_pos_y = min(self._min_pos_y, s[1])
            self._max_pos_y = max(self._max_pos_y, s[1])

        self._grid = []
        rect_w = float(self._max_pos_x - self._min_pos_x) / self.gridWidth
        rect_h = float(self._max_pos_y - self._min_pos_y) / self.gridHeight
        for i in range(self.gridWidth):
            self._grid.append([])
            for j in range(self.gridHeight):
                x = self._min_pos_x + rect_w * i
                y = self._min_pos_y + rect_h * j
                el = self.create_rectangle(x, y, x+rect_w, y+rect_h, tags=['grid'], width=0)
                self._grid[i].append(el)
        self.tag_lower(['grid']) # move all grid elements to back


        # calculate scaling necessary to apply

        self.move("all", self._border - self._min_pos_x, self._border - self._min_pos_y)

        wscale = self.width / float(self._max_pos_x - self._min_pos_x + 2 * self._border)
        hscale = self.height / float(self._max_pos_y - self._min_pos_y + 2 * self._border)
        scale = min(wscale, hscale)
        self.scale("all", 0, 0, scale, scale)

        self.tag_bind('sensor', '<ButtonPress-1>', self.on_click)
        self.tag_bind('led', '<ButtonPress-1>', self.on_click)
        pass


class LightSkinGridView(tk.Frame):
    _Color = '#eee'
    _LEDColorS = '#5da'
    _SensorColorS = '#fa8'
    _elRadius = 50
    _elScale = 100
    _border = 100

    def __init__(self, parent, skin: LightSkin, display_function: Callable[[float], float] = lambda x: x, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.skin = skin
        self.displayFunction = display_function

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
            for j, (f, tt) in enumerate(l):
                c = self._Color
                if i == self.skin.selectedLED:
                    c = self._LEDColorS
                if j == self.skin.selectedSensor:
                    c = self._SensorColorS
                val = self.skin.forwardModel.getSensorValue(j, i)
                v = int(self.displayFunction(val) * 255)
                valcol = "#%02x%02x%02x" % (v, v, v)
                f.configure(highlightbackground=c, bg=valcol)
                tt.text = "%.2f%%" % (val*100)

    def _build(self):
        self._sensors: List[tk.Button] = []
        self._leds: List[tk.Button] = []
        self._measurements: List[List[Tuple[tk.Frame, ToolTip]]] = []

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
                def cmd(e, i=i, j=j):
                    self.skin.selectedLED = i
                    self.skin.selectedSensor = j
                f = tk.Frame(self, bg='#fff', highlightbackground=self._Color, highlightthickness=1)
                toolTip = ToolTip.createToolTip(f, 'None')
                f.bind('<ButtonPress-1>', cmd)
                f.grid(column=i + 1, row=j + 1, sticky='NESW')
                self._measurements[i].append((f, toolTip))

        pass
