#!/usr/bin/python3

import csv
import time

import tkinter as tk

import math

from Algorithm.RayInfluenceModels.DirectSampledRayGridInfluenceModel import DirectSampledRayGridInfluenceModel
from Algorithm.Reconstruction.LogarithmicLinSysOptimize import LogarithmicLinSysOptimize
from Algorithm.Reconstruction.LogarithmicLinSysOptimize2 import LogarithmicLinSysOptimize2
from Algorithm.Reconstruction.SimpleRepeatedDistributeBackProjection import SimpleRepeatedDistributeBackProjection
from Algorithm.Reconstruction.SimpleRepeatedLogarithmicBackProjection import SimpleRepeatedLogarithmicBackProjection
from LightSkin import LightSkin, ValueMap
import GUI.Views as views

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

recSize = 10
repetitions = 20

ls.forwardModel = SimpleProportionalForwardModel(ls, DirectSampledRayGridInfluenceModel())
ls.backwardModel = SimpleBackProjection(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel())
repeated = SimpleRepeatedLogarithmicBackProjection(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel(), repetitions)
repeated2 = SimpleRepeatedDistributeBackProjection(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel(), repetitions)

linsys = LogarithmicLinSysOptimize2(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel())

ls.backwardModel.calculate()

start_time = time.time()
repeated.calculate()
t = time.time() - start_time
print("Total time needed for calculation: %f " % t)

start_time = time.time()
repeated2.calculate()
t = time.time() - start_time
print("Total time needed for calculation: %f " % t)

start_time = time.time()
linsys.calculate()
t = time.time() - start_time
print("Total time needed for calculation: %f " % t)

# print(ls.sensors)
# print(ls.LEDs)
# print(flush=True)

# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Simulation')
window.minsize(900, 300)

topViewsFrame = tk.Frame(window)
topViewsFrame.pack(side=tk.TOP)
topViews2Frame = tk.Frame(window)
topViews2Frame.pack(side=tk.TOP)

topViewTransl = views.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                                     width=300, height=300,
                                     measurable_grid=ls.translucencyMap,
                                     # display_function=lambda x: x
                                     )
topViewTransl.pack(side=tk.LEFT)

topView = views.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                               width=300, height=300,
                               gridWidth=50, gridHeight=50,
                               # display_function=math.sqrt,
                               measure_function=ls.forwardModel.measureAtPoint
                               )
topView.pack(side=tk.LEFT)

topViewReconstructed = views.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                                            width=300, height=300,
                                            measurable_grid=ls.backwardModel,
                                            display_function=lambda x: x ** 10,
                                            )
topViewReconstructed.pack(side=tk.LEFT)

topViewReconstructed2 = views.LightSkinTopView(topViews2Frame, ls, highlightbackground='#aaa', highlightthickness=1,
                                             width=300, height=300,
                                             measurable_grid=repeated,
                                             display_function=lambda x: x**2,
                                             )
topViewReconstructed2.pack(side=tk.LEFT)



topViewReconstructed3 = views.LightSkinTopView(topViews2Frame, ls, highlightbackground='#aaa', highlightthickness=1,
                                             width=300, height=300,
                                             measurable_grid=repeated2,
                                             display_function=lambda x: x**2,
                                             )
topViewReconstructed3.pack(side=tk.LEFT)


topViewReconstructed4 = views.LightSkinTopView(topViews2Frame, ls, highlightbackground='#aaa', highlightthickness=1,
                                             width=300, height=300,
                                             measurable_grid=linsys,
                                             display_function=lambda x: x**2,
                                             )
topViewReconstructed4.pack(side=tk.LEFT)

gridView = views.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                 display_function=math.sqrt
                                 )
gridView.pack(side=tk.BOTTOM)

# topViewReconstructed.postscript(file='Testfile.ps')

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
