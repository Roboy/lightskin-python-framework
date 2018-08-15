from functools import reduce
from typing import List

from ..LightSkin import LightSkin, Calibration


class SimpleCalibration(Calibration):
    """ A simple calibration that takes a snapshot of sensor values as the calibration values """

    def __init__(self, ls: LightSkin):
        super().__init__(ls)
        self.isCalibrated = False
        self._calibration: List[List[float]] = []

    def __current_hash__(self):
        """ Returns a hash of the current calibration status """
        calib_hash = reduce(
            lambda h, l: hash((h,
                               reduce(
                                   lambda h2, el: hash((h2, el)),
                                   l, 0))),
            self._calibration, 0)
        return hash((super().current_hash(), calib_hash))

    def calibrate(self):
        """ Apply the values currently available in the skins default forward model as calibration values """
        self._calibration: List[List[float]] = []
        for i in range(len(self.ls.LEDs)):
            self._calibration.append([])
            for j in range(len(self.ls.sensors)):
                self._calibration[i].append(self.ls.forwardModel.getSensorValue(j, i))
        self.isCalibrated = True
        pass

    def expectedSensorValue(self, sensor: int, led: int) -> float:
        return self._calibration[led][sensor]
