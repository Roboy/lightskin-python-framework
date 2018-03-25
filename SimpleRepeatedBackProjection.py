import math

from LightSkin import LightSkin, Calibration
from SimpleBackProjection import SimpleBackProjection


class SimpleRepeatedBackProjection(SimpleBackProjection):

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int, calibration: Calibration):
        super().__init__(ls, gridWidth, gridHeight, calibration)
        self._bufGrid = []

    def calculate(self):

        # reset internal buffer
        self._bufGrid = []
        for i in range(self.gridWidth):
            self._bufGrid.append([1.0] * self.gridHeight)

        for i in range(20):
            self._calculate_iteration()
            print("Iteration %i" % i)

        # update actual map
        self.grid = self._bufGrid

        return True

    def _calculate_iteration(self):

        self._tmpGrid = []
        self._tmpGridWeights = []
        for i in range(self.gridWidth):
            self._tmpGrid.append([0.0] * self.gridHeight)
            self._tmpGridWeights.append([0.0] * self.gridHeight)

        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                expectedVal = self.calibration.expectedSensorValue(i_s, i_l)
                if expectedVal > self.MIN_SENSITIVITY:
                    translucencyFactor = val / expectedVal
                    dFactor = translucencyFactor / self.__currentTranslucencyFactor(i_s, i_l)
                    self._backProject(i_s, i_l, dFactor)

        for i_l, (line, lineWeighs) in enumerate(zip(self._tmpGrid, self._tmpGridWeights)):
            for i, w in enumerate(lineWeighs):
                # we need to manipulate values
                val = self.UNKNOWN_VAL
                if w > 0:
                    val = line[i] / w
                # val = val ** 10
                # Weighting the value by the knowledge we have
                # To reduce "noise" in low-knowledge-areas
                val = self.UNKNOWN_VAL + (val - self.UNKNOWN_VAL) * (1 - 1 / (w * self.sampleDistance + 1))
                line[i] = val
                self._bufGrid[i_l][i] = max(0.0, min(1.0, self._bufGrid[i_l][i] * val))

        return True

    def __currentTranslucencyFactor(self, sensor: int, led: int) -> float:
        LED = self.ls.LEDs[led]
        Sensor = self.ls.sensors[sensor]

        dx = float(Sensor[0] - LED[0])
        dy = float(Sensor[1] - LED[1])

        dist = math.sqrt(dx ** 2 + dy ** 2)
        translucencyMul = 1

        if dist > 0:
            # sample translucency map
            dxStep = dx / dist * self.sampleDistance
            dyStep = dy / dist * self.sampleDistance
            steps = dy / dyStep if dxStep == 0 else dx / dxStep
            # print("Sampling for LED %i with %i steps" % (led, steps))
            for i in range(int(steps)):
                translucencyMul *= self._measureBufAtPoint(LED[0] + i * dxStep, LED[1] + i * dyStep) \
                                   ** self.sampleDistance

        return max(0.0, min(1.0, translucencyMul))

    def _measureBufAtPoint(self, x: float, y: float) -> float:
        i = int((x - self._min_pos_x) / self._rect_w)
        j = int((y - self._min_pos_y) / self._rect_h)

        i = max(0, min(self.gridWidth - 1, i))
        j = max(0, min(self.gridHeight - 1, j))

        # print("displaying at %i %i: %f" % (i, j, self.grid[i][j]))

        return max(0.0, min(1.0, self._bufGrid[i][j]))
