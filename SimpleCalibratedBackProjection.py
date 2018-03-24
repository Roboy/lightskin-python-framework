import math
from typing import List

from LightSkin import BackwardModel, LightSkin
from SimpleProportionalBackProjection import SimpleProportionalBackProjection


class SimpleCalibratedBackProjection(SimpleProportionalBackProjection):

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

    def _expectedSensorValue(self, sensor: int, led: int) -> float:
        return self._calibration[led][sensor]
