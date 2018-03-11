#!/usr/bin/python3

import time
from datetime import datetime
import requests
import importlib, types
import queue
import signal
import csv
from threading import Thread
import os, sys, traceback

import tkinter as tk

from LightSkin import LightSkin
import LightSkinViz as Viz

ls = LightSkin()

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

topView = Viz.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1)
topView.pack()

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
