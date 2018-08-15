import math

from ...LightSkin import BackwardModel


class SimpleDumbProportionalBackProjection(BackwardModel):
    sampleDistance = 0.125
    MIN_SENSITIVITY = 0.05

    def calculate(self) -> bool:

        self.grid = []
        for i in range(self.gridWidth):
            self.grid.append([1.0] * self.gridHeight)

        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                expectedVal = self._expectedSensorValue(i_s, i_l)
                if expectedVal > self.MIN_SENSITIVITY:
                    translucencyFactor = val / expectedVal
                    self._backProject(i_s, i_l, translucencyFactor)

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

            sampleFactor = factor ** (1/steps)
            #print('Sample factor for LED %i -> Sensor %i: %f %i => %f' % (led, sensor, factor, steps, sampleFactor))

            # print("Sampling for LED %i with %i steps" % (led, steps))
            for i in range(int(steps)):
                # find corresponding grid element for this sample
                x = LED[0] + i * dxStep
                y = LED[1] + i * dyStep
                x_i = int((x - self._min_pos_x) / self._rect_w)
                y_i = int((y - self._min_pos_y) / self._rect_h)

                x_i = max(0, min(self.gridWidth - 1, x_i))
                y_i = max(0, min(self.gridHeight - 1, y_i))

                self.grid[x_i][y_i] *= sampleFactor
                #print('Influencing %i %i = %f' % (x_i, y_i, self.grid[x_i][y_i]))


    def _expectedSensorValue(self, sensor: int, led: int) -> float:
        sensor = self.ls.sensors[sensor]
        LED = self.ls.LEDs[led]

        dx = float(sensor[0] - LED[0])
        dy = float(sensor[1] - LED[1])

        dist = math.sqrt(dx ** 2 + dy ** 2)

        dist = max(dist, 0.1)
        val = 4 / dist

        return max(0.0, min(1.0, val))


    def measureAtPoint(self, x: float, y: float) -> float:
        i = int((x - self._min_pos_x) / self._rect_w)
        j = int((y - self._min_pos_y) / self._rect_h)

        i = max(0, min(self.gridWidth-1, i))
        j = max(0, min(self.gridHeight-1, j))

        #print("displaying at %i %i: %f" % (i, j, self.grid[i][j]))

        return max(0.0, min(1.0, self.grid[i][j]))
