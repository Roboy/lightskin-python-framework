import math

from ..RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from ...LightSkin import BackwardModel, LightSkin, Calibration


class SimpleBackProjection(BackwardModel):
    """ Implements the back projection approach where the value is equally distributed along each ray """

    MIN_SENSITIVITY = 0.02
    UNKNOWN_VAL = 1.0

    def __init__(self,
                 ls: LightSkin,
                 gridWidth: int,
                 gridHeight: int,
                 calibration: Calibration,
                 ray_model: RayGridInfluenceModel):
        super().__init__(ls, gridWidth, gridHeight, calibration)
        self._tmpGrid = []
        self._tmpGridWeights = []
        self.rayModel: RayGridInfluenceModel = ray_model
        self.rayModel.gridDefinition = self.gridDefinition

    def calculate(self) -> bool:

        self._tmpGrid = self.gridDefinition.makeGridFilledWith(0.0)
        self._tmpGridWeights = self.gridDefinition.makeGridFilledWith(0.0)

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
                # val = val ** 10
                # Weighting the value by the knowledge we have
                # To reduce "noise" in low-knowledge-areas
                #val = self.UNKNOWN_VAL + (val - self.UNKNOWN_VAL) * (1 - 1 / (w * self.sampleDistance + 1))
                line[i] = val

        self.grid = self._tmpGrid

        return True

    def _backProject(self, sensor: int, led: int, factor: float):
        ray = self.ls.getRayFromLEDToSensor(sensor, led)

        cells = self.rayModel.getInfluencesForRay(ray)

        dfactor = factor ** (1 / ray.length)

        for (i, j), w in cells:
            # weighted factorization
            self._tmpGrid[i][j] += dfactor * w
            self._tmpGridWeights[i][j] += w
