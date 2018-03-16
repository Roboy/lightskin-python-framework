#!/usr/bin/python3

import time
from datetime import datetime
import importlib, types
import queue
import signal
import csv
from threading import Thread
import os, sys, traceback

import tkinter as tk

from LightSkin import LightSkin
import LightSkinViz as Viz

from SimpleProportionalForwardModel import SimpleProportionalForwardModel

ls = LightSkin()
ls.forwardModel = SimpleProportionalForwardModel(ls)

# LOAD Sensor and LED coordinates from CSV

with open('sensors.csv', 'r') as csvfile:
    read = csv.reader(csvfile)
    for r in read:
        s = (float(r[0]), float(r[1]))
        ls.sensors.append(s)
#
with open('leds.csv', 'r') as csvfile:
    read = csv.reader(csvfile)
    for r in read:
        s = (float(r[0]), float(r[1]))
        ls.LEDs.append(s)
#



print(ls.sensors)
print(ls.LEDs)
print(flush=True)


# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Simulation')
window.minsize(400, 300)

topView = Viz.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1,
                               gridWidth=50, gridHeight=50,
                               #display_function=lambda x: x,
                               measure_function=ls.forwardModel.measureAtPoint)
topView.pack()

gridView = Viz.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1)
gridView.pack()


window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
