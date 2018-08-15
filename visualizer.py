#!/usr/bin/python3

import csv

import tkinter as tk

from LightSkin.Algorithm.RayInfluenceModels.DirectSampledRayGridInfluenceModel import DirectSampledRayGridInfluenceModel
from LightSkin.Algorithm.Reconstruction.LogarithmicLinSysOptimize2 import LogarithmicLinSysOptimize2
from LightSkin.LightSkin import LightSkin
from LightSkin.GUI import Views

# from SimpleProportionalForwardModel import SimpleProportionalForwardModel
from LightSkin.Algorithm.ForwardModels.ArduinoConnectorForwardModel import ArduinoConnectorForwardModel
from LightSkin.Algorithm.SimpleCalibration import SimpleCalibration
import serial.tools.list_ports


# Source: https://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
def transposed(lists):
    if not lists:
        return []
    return list(map(lambda *row: list(row), *lists))


# Main Code

ports = list(serial.tools.list_ports.comports())
port = None
for p in ports:
    print('Checking port %s / %s' % (p[0], p[1]))
    if "uino" in p[1].lower():  # Find "ardUINO" and "genUINO" boards
        port = p
        break

if port is None:
    print('Could not find a connected Arduino')
    exit(0)

print('Using the Arduino connected on:')
print(port[0] + ' / ' + port[1])

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

recResolution = 8

calibration = SimpleCalibration(ls)

arduinoConnector = ArduinoConnectorForwardModel(ls, port[0], 1000000)
backwardModel = LogarithmicLinSysOptimize2(ls,
                                           recResolution, recResolution,
                                           calibration,
                                           DirectSampledRayGridInfluenceModel())

ls.forwardModel = arduinoConnector
ls.backwardModel = backwardModel

# print(ls.sensors)
# print(ls.LEDs)
# print(flush=True)

pressure_colormap = 'nipy_spectral'

# Build Window with widgets etc...
window = tk.Tk()
window.title('Light Skin Visualization')
window.minsize(900, 300)

gridView = Views.LightSkinGridView(window, ls, width=400, height=400, highlightbackground='#aaa', highlightthickness=1,
                                   display_function=Views.Colorscales.MPColorMap('inferno', lambda x: x ** 0.3)
                                   )
gridView.pack(side=tk.LEFT)

topViewReconstructed = Views.LightSkinTopView(window, ls, highlightbackground='#aaa', highlightthickness=1,
                                              width=500, height=500,
                                              measurable_grid=ls.backwardModel,
                                              display_function=Views.Colorscales.Grayscale(lambda x: x ** 2)  # MPColorMap(pressure_colormap)
                                              )
topViewReconstructed.pack(side=tk.RIGHT)


def onUpdate():
    if not calibration.isCalibrated:
        calibration.calibrate()
    backwardModel.calculate()
    ls.onChange('values')


arduinoConnector.onUpdate += onUpdate

window.mainloop()

# Main program logic follows:
# if __name__ == '__main__':
#
