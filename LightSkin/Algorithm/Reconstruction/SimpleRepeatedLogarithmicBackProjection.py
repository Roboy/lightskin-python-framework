import math
from typing import List, Tuple

from ..RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from ...LightSkin import LightSkin, Calibration, BackwardModel


class SimpleRepeatedLogarithmicBackProjection(BackwardModel):
    """ Almost equal to the SimpleRepeatedDistributeBackProjection but transferred to logarithmic space """
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
        """ Contains the weights while they are being built in log space """
        self.rayModel: RayGridInfluenceModel = ray_model
        self.rayModel.gridDefinition = self.gridDefinition
        self.repetitions: int = repetitions

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
        """ cells that are open for the next round """

        rest_translucency = translucency
        """ Translucency delta that still needs to be distributed """
        d_transl = .0
        """ translucency per distance in the current iteration;
            translucency delta currently applied to all cells that are left """
        cells_left: List[Tuple[Tuple[int, int], float]] = []
        """ Cells that can still take more translucency """
        cells_finished: List[Tuple[Tuple[int, int], float, float]] = []
        """ Cells for which the resulting translucency delta has already been calculated """

        while (abs(rest_translucency) > .00001) and len(cells) > 0:
            # While there is still transl. to be distributed and we still have cells that can take transl

            weight_sum = sum(map(lambda el: el[1], cells))
            total_transl = rest_translucency + (d_transl * weight_sum)
            """ total translucency left =
                rest_translucency needed to be applied + translucency currently applied on all cells that are still open
            """
            d_transl = total_transl / weight_sum
            rest_translucency = .0

            for (i, j), w in cells:
                if self._bufGrid[i][j] + d_transl > 0:  # max out at 0; cell can't take anymore
                    t = -self._bufGrid[i][j]
                    # t thus us the max the cell can still take
                    rest_translucency += (d_transl - t) * w
                    # 'add up' the remaining transl that still needs to be distributed
                    cells_finished.append(((i, j), w, t))
                    # The resulting transl. delta for this cell has been determined; no more work needed
                else:
                    # add cell to list of cells that could potentially still take more transl
                    cells_left.append(((i, j), w))

            cells = cells_left
            cells_left = []

        # all remaining cells get the current d_transl
        for (i, j), w in cells:
            cells_finished.append(((i, j), w, d_transl))

        for (i, j), w, f in cells_finished:
            self._tmpGrid[i][j] += f * w
            self._tmpGridWeights[i][j] += w
