import math
from typing import List

from LightSkin import BackwardModel, LightSkin
from SimpleProportionalBackProjection import SimpleProportionalBackProjection


class SimpleCalibratedBackProjection(SimpleProportionalBackProjection):
    sampleDistance = 0.125
    MIN_SENSITIVITY = 0.05

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int):
        super().__init__(ls, gridWidth, gridHeight)
        self.isCalibrated = False

    def calibrate(self):
        self._calibration: List[List[float]] = []
        for i in range(len(self.ls.LEDs)):
            self._calibration.append([])
            for j in range(len(self.ls.sensors)):
                self._calibration[i].append(self.ls.forwardModel.getSensorValue(j, i))
        self.isCalibrated = True
        pass

    def calculate(self) -> bool:

        self.grid = []
        for i in range(self.gridWidth):
            self.grid.append([1.0] * self.gridHeight)

        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                expectedVal = self._calibration[i_l][i_s]
                if expectedVal > self.MIN_SENSITIVITY:
                    translucencyFactor = val / expectedVal
                    self._backProject(i_s, i_l, translucencyFactor)

        return True
