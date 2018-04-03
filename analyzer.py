#!/usr/bin/python3

import csv
import time

import tkinter as tk

import math

from Algorithm.Analyze.SensitivityMap import SensitivityMap
from Algorithm.RayInfluenceModels.DirectSampledRayGridInfluenceModel import DirectSampledRayGridInfluenceModel
from LightSkin import LightSkin, ValueMap
import GUI.Views as Views

from Algorithm.ForwardModels.SimpleProportionalForwardModel import SimpleProportionalForwardModel, \
    SimpleIdealProportionalCalibration
from Algorithm.Reconstruction.SimpleBackProjection import SimpleBackProjection

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

gridVals = []
with open('translucency.csv', 'r') as csvfile:
    read = csv.reader(csvfile)
    for r in read:
        vals = list(map(float, r))
        gridVals.append(vals)

translucency = ValueMap(ls.getGridArea(), grid=transposed(gridVals))
ls.translucencyMap = translucency

resolution = 100

ls.forwardModel = SimpleProportionalForwardModel(ls, DirectSampledRayGridInfluenceModel())

sensitivity = SensitivityMap(ls, resolution,
                             resolution,
                             DirectSampledRayGridInfluenceModel())


start_time = time.time()
sensitivity.calculate()
t = time.time() - start_time
print("Total time needed for calculation: %f " % t)




# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Analysis')
window.minsize(300, 300)


sensitivity_view = Views.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1,
                                       width=500, height=500,
                                       measurable_grid=sensitivity,
                                       display_function=Views.Colorscales.MPColorMap('gnuplot')
                                       )
sensitivity_view.pack(side=tk.LEFT)

# topViewReconstructed.postscript(file='Testfile.ps')

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
