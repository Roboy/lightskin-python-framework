from typing import List

from LightSkin import LightSkin, Calibration


class SimpleCalibration(Calibration):

    def __init__(self, ls: LightSkin):
        super().__init__(ls)
        self.isCalibrated = False
        self._calibration: List[List[float]] = []

    def calibrate(self):
        self._calibration: List[List[float]] = []
        for i in range(len(self.ls.LEDs)):
            self._calibration.append([])
            for j in range(len(self.ls.sensors)):
                self._calibration[i].append(self.ls.forwardModel.getSensorValue(j, i))
        self.isCalibrated = True
        pass

    def expectedSensorValue(self, sensor: int, led: int) -> float:
        return self._calibration[led][sensor]
