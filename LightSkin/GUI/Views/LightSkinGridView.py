import tkinter as tk
from typing import List, Callable, Tuple

from . import Colorscales
from .Color import Color
from ..TKinterToolTip import ToolTip
from ...LightSkin import LightSkin


class LightSkinGridView(tk.Frame):
    """ Displays the sensor data from the default forward model of the skin in a grid.
        Columns represent LEDs, rows sensors."""
    _Color = '#eee'
    _LEDColorS = '#5da'
    _SensorColorS = '#fa8'
    _elRadius = 50
    _elScale = 100
    _border = 100

    def __init__(self, parent, skin: LightSkin,
                 display_function: Callable[[float], Color] = Colorscales.Grayscale(lambda x: x),
                 **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.skin = skin
        self.displayFunction: Callable[[float], Color] = display_function

        self._build()
        skin.onChange += lambda *a, **kwa: self.after_idle(self.updateVisuals)  # send to main thread
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
                col = self.displayFunction(val)
                f.configure(highlightbackground=c, bg=col.toHex())
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