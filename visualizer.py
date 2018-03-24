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

import math

from LightSkin import LightSkin, LSValueMap
import LightSkinViz as Viz

# from SimpleProportionalForwardModel import SimpleProportionalForwardModel
from ArduinoConnectorForwardModel import ArduinoConnectorForwardModel
# from SimpleProportionalBackProjection import SimpleProportionalBackProjection
from SimpleCalibratedBackProjection import SimpleCalibratedBackProjection


# Source: https://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
def transposed(lists):
    if not lists:
        return []
    return list(map(lambda *row: list(row), *lists))


# Main Code

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

arduinoConnector = ArduinoConnectorForwardModel(ls, 'COM3', 1000000)

ls.forwardModel = arduinoConnector
ls.backwardModel = SimpleCalibratedBackProjection(ls, 10, 10)

# print(ls.sensors)
# print(ls.LEDs)
# print(flush=True)

# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Simulation')
window.minsize(900, 300)

gridView = Viz.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                 display_function=math.sqrt

                                 )
gridView.pack(side=tk.LEFT)

topViewReconstructed = Viz.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1,
                                            width=500, height=500,
                                            gridWidth=ls.backwardModel.gridWidth,
                                            gridHeight=ls.backwardModel.gridHeight,
                                            # display_function=math.sqrt,
                                            measure_function=ls.backwardModel.measureAtPoint
                                            )
topViewReconstructed.pack(side=tk.RIGHT)


def onUpdate():
    gridView.updateVisuals()
    topViewReconstructed.updateVisuals()


arduinoConnector.onUpdate += onUpdate

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
