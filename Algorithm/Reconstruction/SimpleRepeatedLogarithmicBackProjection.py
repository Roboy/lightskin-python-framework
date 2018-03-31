import math
from typing import List

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from LightSkin import LightSkin, Calibration, BackwardModel


class SimpleRepeatedLogarithmicBackProjection(BackwardModel):
    MIN_SENSITIVITY = 0.02
    UNKNOWN_VAL = 0.0

    def __init__(self, ls: LightSkin,
                 gridWidth: int,
                 gridHeight: int,
                 calibration: Calibration,
                 ray_model: RayGridInfluenceModel,
                 repetitions: int = 20):
        super().__init__(ls, gridWidth, gridHeight, calibration)
        self._tmpGrid = []
        self._tmpGridWeights = []
        self._bufGrid: List[List[float]] = []
        self.rayModel: RayGridInfluenceModel = ray_model
        self.rayModel.gridDefinition = self.gridDefinition
        self.repetitions: int = repetitions
        """ Contains the weights while they are being built in log space """

    def calculate(self):

        # reset internal buffer
        self._bufGrid = []
        for i in range(self.gridDefinition.cellsX):
            self._bufGrid.append([0.0] * self.gridDefinition.cellsY)

        for i in range(self.repetitions):
            self._calculate_iteration()
            print("Iteration %i" % i)

        # update actual map
        for i, line in enumerate(self._bufGrid):
            for j, c in enumerate(line):
                # Actual grid is not in logarithm space but in normal
                self.grid[i][j] = math.exp(self._bufGrid[i][j])
                # print("Resulting value %i %i : %f" % (i, j, self.grid[i][j]))

        return True

    def _calculate_iteration(self):

        self._tmpGrid = []
        self._tmpGridWeights = []
        for i in range(self.gridDefinition.cellsX):
            self._tmpGrid.append([0.0] * self.gridDefinition.cellsY)
            self._tmpGridWeights.append([0.0] * self.gridDefinition.cellsY)

        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                expected_val = self.calibration.expectedSensorValue(i_s, i_l)
                if expected_val > self.MIN_SENSITIVITY:
                    val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                    translucency = math.log(val / expected_val)
                    d_translucency = translucency - self._currentBufTranslucency(i_s, i_l)
                    self._backProject(i_s, i_l, d_translucency)

        for i, (row, rowWeighs) in enumerate(zip(self._tmpGrid, self._tmpGridWeights)):
            for j, w in enumerate(rowWeighs):
                # we need to manipulate values
                val = self.UNKNOWN_VAL
                if w > 0:
                    val = row[j] / w
                row[j] = val
                self._bufGrid[i][j] = min(0.0, self._bufGrid[i][j] + val)

        return True

    def _currentBufTranslucency(self, sensor: int, led: int) -> float:
        ray = self.ls.getRayFromLEDToSensor(sensor, led)
        cells = self.rayModel.getInfluencesForRay(ray)

        translucency = 0
        for (i, j), w in cells:
            # weighted factorization
            translucency += self._bufGrid[i][j] * w

        return min(0.0, translucency)

    def _backProject(self, sensor: int, led: int, translucency: float):
        ray = self.ls.getRayFromLEDToSensor(sensor, led)

        cells = self.rayModel.getInfluencesForRay(ray)

        d_transl = translucency / ray.length

        # print("Projecting ray %i %i : %f" % (sensor, led, translucency))
        for (i, j), w in cells:
            # weighted factorization
            self._tmpGrid[i][j] += d_transl * w
            self._tmpGridWeights[i][j] += w

            # print("Influencing cell %i %i : %f" % (i, j, self._tmpGrid[i][j]))
