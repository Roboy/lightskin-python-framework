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

from SimpleProportionalForwardModel import SimpleProportionalForwardModel, SimpleIdealProportionalCalibration
from SimpleBackProjection import SimpleBackProjection
from SimpleDumbProportionalBackProjection import SimpleDumbProportionalBackProjection


# Source: https://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
from SimpleRepeatedBackProjection import SimpleRepeatedBackProjection


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

gridVals = []
with open('translucency.csv', 'r') as csvfile:
    read = csv.reader(csvfile)
    for r in read:
        vals = list(map(float, r))
        gridVals.append(vals)

translucency = LSValueMap(ls, grid=transposed(gridVals))
ls.translucencyMap = translucency


recSize = 10

ls.forwardModel = SimpleProportionalForwardModel(ls)
ls.backwardModel = SimpleBackProjection(ls, recSize, recSize, SimpleIdealProportionalCalibration(ls))
repeated = SimpleRepeatedBackProjection(ls, recSize, recSize, SimpleIdealProportionalCalibration(ls))


ls.backwardModel.calculate()
repeated.calculate()


# print(ls.sensors)
# print(ls.LEDs)
# print(flush=True)

# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Simulation')
window.minsize(900, 300)

topViewsFrame = tk.Frame(window)
topViewsFrame.pack(side=tk.TOP)

topViewTransl = Viz.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                                     width=300, height=300,
                                     gridWidth=ls.translucencyMap.gridWidth, gridHeight=ls.translucencyMap.gridHeight,
                                     # display_function=lambda x: x,
                                     measure_function=ls.translucencyMap.measureAtPoint
                                     )
topViewTransl.pack(side=tk.LEFT)

topView = Viz.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                               width=300, height=300,
                               gridWidth=50, gridHeight=50,
                               # display_function=math.sqrt,
                               measure_function=ls.forwardModel.measureAtPoint
                               )
topView.pack(side=tk.LEFT)



topViewReconstructed = Viz.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                               width=300, height=300,
                               gridWidth=ls.backwardModel.gridWidth, gridHeight=ls.backwardModel.gridHeight,
                               display_function=lambda x: x ** 10,
                               measure_function=ls.backwardModel.measureAtPoint
                               )
topViewReconstructed.pack(side=tk.LEFT)



topViewReconstructed2 = Viz.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                               width=300, height=300,
                               gridWidth=repeated.gridWidth, gridHeight=repeated.gridHeight,
                               display_function=lambda x: x,
                               measure_function=repeated.measureAtPoint
                               )
topViewReconstructed2.pack(side=tk.LEFT)


gridView = Viz.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                 display_function=math.sqrt
                                 )
gridView.pack(side=tk.BOTTOM)

#topViewReconstructed.postscript(file='Testfile.ps')

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
