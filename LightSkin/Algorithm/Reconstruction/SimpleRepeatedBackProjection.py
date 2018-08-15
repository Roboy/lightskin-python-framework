import math

from .SimpleBackProjection import SimpleBackProjection
from ..RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from ...LightSkin import LightSkin, Calibration


class SimpleRepeatedBackProjection(SimpleBackProjection):
    """ Improves on the back projection by iteratively calculating the expected values for the current reconstruction.
        The error to the actual measurement then once again gets backprojected.
        This is repeated n times
    """

    def __init__(self, ls: LightSkin,
                 gridWidth: int,
                 gridHeight: int,
                 calibration: Calibration,
                 ray_model: RayGridInfluenceModel,
                 repetitions: int = 20):
        super().__init__(ls, gridWidth, gridHeight, calibration, ray_model)
        self._bufGrid = []
        self.repetitions: int = repetitions

    def calculate(self):

        # reset internal buffer
        self._bufGrid = self.gridDefinition.makeGridFilledWith(1.0)

        for i in range(self.repetitions):
            self._calculate_iteration()
            print("Iteration %i" % i)

        # update actual map
        self.grid = self._bufGrid

        return True

    def _calculate_iteration(self):

        self._tmpGrid = self.gridDefinition.makeGridFilledWith(0.0)
        self._tmpGridWeights = self.gridDefinition.makeGridFilledWith(0.0)

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
                #val = self.UNKNOWN_VAL + (val - self.UNKNOWN_VAL) * (1 - 1 / (w * self.sampleDistance + 1))
                line[i] = val
                self._bufGrid[i_l][i] = max(0.0, min(1.0, self._bufGrid[i_l][i] * val))

        return True

    def __currentTranslucencyFactor(self, sensor: int, led: int) -> float:
        ray = self.ls.getRayFromLEDToSensor(sensor, led)
        cells = self.rayModel.getInfluencesForRay(ray)

        translucencyMul = 1
        for (i, j), w in cells:
            # weighted factorization
            translucencyMul *= self._bufGrid[i][j] ** w

        return max(0.0, min(1.0, translucencyMul))
