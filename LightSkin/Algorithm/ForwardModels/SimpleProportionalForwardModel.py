import math

from ..RayInfluenceModels.RayInfluenceModel import Ray, RayGridInfluenceModel
from ...LightSkin import ForwardModel, Calibration, LightSkin


class SimpleProportionalForwardModel(ForwardModel):
    """ Calculates the light received at a location using the given RayGridInfluenceModel.
        Assumes a inverse proportional falloff of the light with distance. """

    sampleDistance = 0.125

    def __init__(self, ls: LightSkin, ray_model: RayGridInfluenceModel):
        super().__init__(ls)
        self.rayModel = ray_model
        self.rayModel.gridDefinition = self.ls.translucencyMap.gridDefinition

    def measureLEDAtPoint(self, x: float, y: float, led: int = -1) -> float:
        (l_x, l_y) = self.ls.LEDs[led if led >= 0 else self.ls.selectedLED]
        ray = Ray(l_x, l_y, x, y)

        cells = self.rayModel.getInfluencesForRay(ray)
        dist = ray.length

        translucencyMul = 1

        for (i, j), w in cells:
            # weighted factorization
            translucencyMul *= self.ls.translucencyMap.grid[i][j] ** w

        dist = max(dist, 0.1)
        val = 4 / dist
        val *= translucencyMul

        #print("Calculated value for LED %i (%i, %i) to (%i, %i) Distance: %i; val: %f" % (led, LED[0], LED[1], x, y, dist, val))
        return max(0.0, min(1.0, val))


class SimpleIdealProportionalCalibration(Calibration):
    """ The ideal calibration values for the SimpleProportionalForwardModel """

    def __hash__(self):
        return hash(self.__class__.__name__)  # all instances of this class are equivalent

    def expectedSensorValue(self, sensor: int, led: int) -> float:
        ray = self.ls.getRayFromLEDToSensor(sensor, led)

        dist = max(ray.length, 0.1)
        val = 4 / dist

        return max(0.0, min(1.0, val))
