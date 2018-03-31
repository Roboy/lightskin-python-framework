#!/usr/bin/python3

import csv

import tkinter as tk

import math

from Algorithm.RayInfluenceModels.DirectSampledRayGridInfluenceModel import DirectSampledRayGridInfluenceModel
from Algorithm.Reconstruction.SimpleRepeatedDistributeBackProjection import SimpleRepeatedDistributeBackProjection
from Algorithm.Reconstruction.SimpleRepeatedLogarithmicBackProjection import SimpleRepeatedLogarithmicBackProjection
from LightSkin import LightSkin, ValueMap
from GUI import LightSkinViz as Viz

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

ls.forwardModel = SimpleProportionalForwardModel(ls, DirectSampledRayGridInfluenceModel())
ls.backwardModel = SimpleBackProjection(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel())
repeated = SimpleRepeatedBackProjection(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel(), 50)
repeated2 = SimpleRepeatedLogarithmicBackProjection(ls, recSize,
                                        recSize,
                                        SimpleIdealProportionalCalibration(ls),
                                        DirectSampledRayGridInfluenceModel(), 20)

ls.backwardModel.calculate()
repeated.calculate()
repeated2.calculate()

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
                                     measurable_grid=ls.translucencyMap,
                                     # display_function=lambda x: x
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
                                            measurable_grid=ls.backwardModel,
                                            display_function=lambda x: x ** 10,
                                            )
topViewReconstructed.pack(side=tk.LEFT)

topViewReconstructed2 = Viz.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                                             width=300, height=300,
                                             measurable_grid=repeated,
                                             display_function=lambda x: x**2,
                                             )
topViewReconstructed2.pack(side=tk.LEFT)



topViewReconstructed3 = Viz.LightSkinTopView(topViewsFrame, ls, highlightbackground='#aaa', highlightthickness=1,
                                             width=300, height=300,
                                             measurable_grid=repeated2,
                                             display_function=lambda x: x**2,
                                             )
topViewReconstructed3.pack(side=tk.LEFT)

gridView = Viz.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                 display_function=math.sqrt
                                 )
gridView.pack(side=tk.BOTTOM)

# topViewReconstructed.postscript(file='Testfile.ps')

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
