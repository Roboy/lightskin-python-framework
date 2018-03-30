#!/usr/bin/python3

import csv

import tkinter as tk

from Algorithm.RayInfluenceModels.DirectSampledRayGridInfluenceModel import DirectSampledRayGridInfluenceModel
from LightSkin import LightSkin
from GUI import LightSkinViz as Viz

# from SimpleProportionalForwardModel import SimpleProportionalForwardModel
from Algorithm.ForwardModels.ArduinoConnectorForwardModel import ArduinoConnectorForwardModel
from Algorithm.SimpleCalibration import SimpleCalibration


# Source: https://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
from Algorithm.Reconstruction.SimpleRepeatedBackProjection import SimpleRepeatedBackProjection


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

recResolution = 10

calibration = SimpleCalibration(ls)

arduinoConnector = ArduinoConnectorForwardModel(ls, 'COM3', 1000000)
backwardModel = SimpleRepeatedBackProjection(ls,
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

gridView = Viz.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                 display_function=lambda x: min(1.0, x*2) ** 0.25
                                 )
gridView.pack(side=tk.LEFT)

topViewReconstructed = Viz.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1,
                                            width=500, height=500,
                                            measurable_grid=ls.backwardModel,
                                            display_function=lambda x: x ** 10
                                            )
topViewReconstructed.pack(side=tk.RIGHT)


def onUpdate():
    if not calibration.isCalibrated:
        calibration.calibrate()
    backwardModel.calculate()
    gridView.updateVisuals()
    topViewReconstructed.updateVisuals()


arduinoConnector.onUpdate += onUpdate

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
