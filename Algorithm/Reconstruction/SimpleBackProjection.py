import math

from LightSkin import BackwardModel, LightSkin, Calibration


class SimpleBackProjection(BackwardModel):
    sampleDistance = 0.125
    MIN_SENSITIVITY = 0.02
    UNKNOWN_VAL = 1.0

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int, calibration: Calibration):
        super().__init__(ls, gridWidth, gridHeight, calibration)
        self._tmpGrid = []
        self._tmpGridWeights = []

    def calculate(self) -> bool:

        self._tmpGrid = self.gridDefinition.makeFloatGridFilledWith(0.0)
        self._tmpGridWeights = self.gridDefinition.makeFloatGridFilledWith(0.0)

        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                expectedVal = self.calibration.expectedSensorValue(i_s, i_l)
                if expectedVal > self.MIN_SENSITIVITY:
                    translucencyFactor = val / expectedVal
                    self._backProject(i_s, i_l, translucencyFactor)

        for i_l, (line, lineWeighs) in enumerate(zip(self._tmpGrid, self._tmpGridWeights)):
            for i, w in enumerate(lineWeighs):
                # we need to manipulate values
                val = self.UNKNOWN_VAL
                if w > 0:
                    val = line[i] / w
                #val = val ** 10
                # Weighting the value by the knowledge we have
                # To reduce "noise" in low-knowledge-areas
                val = self.UNKNOWN_VAL + (val - self.UNKNOWN_VAL) * (1 - 1/(w*self.sampleDistance+1))
                line[i] = val

        self.grid = self._tmpGrid

        return True


    def _backProject(self, sensor: int, led: int, factor: float):
        Sensor = self.ls.sensors[sensor]
        LED = self.ls.LEDs[led]

        dx = float(Sensor[0] - LED[0])
        dy = float(Sensor[1] - LED[1])

        dist = math.sqrt(dx ** 2 + dy ** 2)

        #print('Backprojecting for grid of size (%i, %i)' % (self.gridWidth, self.gridHeight))

        if dist > 0:
            # project back into translucency map
            dxStep = dx / dist * self.sampleDistance
            dyStep = dy / dist * self.sampleDistance
            steps = dy / dyStep if dxStep == 0 else dx / dxStep

            sampleFactor = factor ** (1/steps)  # We assume all steps have the same factor
            sampleFactor = sampleFactor ** (1/self.sampleDistance)
            #print('Sample factor for LED %i -> Sensor %i: %f %i => %f' % (led, sensor, factor, steps, sampleFactor))

            # print("Sampling for LED %i with %i steps" % (led, steps))
            for i in range(int(steps)):
                # find corresponding grid element for this sample
                x = LED[0] + i * dxStep
                y = LED[1] + i * dyStep

                i, j = self.gridDefinition.getCellAtPoint(x, y)

                self._tmpGrid[i][j] += sampleFactor
                self._tmpGridWeights[i][j] += 1
                #if 50 < x_i < 55 and 5 < y_i < 15:
                #    print('Influencing %i %i = %f' % (x_i, y_i, self._tmpGrid[x_i][y_i]))

