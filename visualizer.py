#!/usr/bin/python3

import csv

import tkinter as tk

from Algorithm.RayInfluenceModels.DirectSampledRayGridInfluenceModel import DirectSampledRayGridInfluenceModel
from Algorithm.Reconstruction.LogarithmicLinSysOptimize import LogarithmicLinSysOptimize
from Algorithm.Reconstruction.LogarithmicLinSysOptimize2 import LogarithmicLinSysOptimize2
from Algorithm.Reconstruction.SimpleRepeatedBackProjection import SimpleRepeatedBackProjection
from Algorithm.Reconstruction.SimpleRepeatedDistributeBackProjection import SimpleRepeatedDistributeBackProjection
from LightSkin import LightSkin
import GUI.Views as Views

# from SimpleProportionalForwardModel import SimpleProportionalForwardModel
from Algorithm.ForwardModels.ArduinoConnectorForwardModel import ArduinoConnectorForwardModel
from Algorithm.SimpleCalibration import SimpleCalibration


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

recResolution = 15

calibration = SimpleCalibration(ls)

arduinoConnector = ArduinoConnectorForwardModel(ls, 'COM3', 1000000)
backwardModel = LogarithmicLinSysOptimize2(ls,
                                           recResolution, recResolution,
                                           calibration,
                                           DirectSampledRayGridInfluenceModel())

ls.forwardModel = arduinoConnector
ls.backwardModel = backwardModel

# print(ls.sensors)
# print(ls.LEDs)
# print(flush=True)

# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Simulation')
window.minsize(900, 300)

gridView = Views.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                   display_function=lambda x: min(1.0, x * 2) ** 0.3
                                   )
gridView.pack(side=tk.LEFT)

topViewReconstructed = Views.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1,
                                              width=500, height=500,
                                              measurable_grid=ls.backwardModel,
                                              display_function=lambda x: x ** 4
                                              )
topViewReconstructed.pack(side=tk.RIGHT)


def onUpdate():
    if not calibration.isCalibrated:
        calibration.calibrate()
    backwardModel.calculate()
    ls.onChange.fire('values')


arduinoConnector.onUpdate += onUpdate

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
