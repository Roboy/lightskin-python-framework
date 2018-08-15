import math
from abc import abstractmethod

from ..RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from ...Helpers.ValueMap import ValueMap
from ...LightSkin import LightSkin


class SensitivityMap(ValueMap):
    """ A map showing the sensitivity of each cell given the current setup """

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int,
                 ray_model: RayGridInfluenceModel,
                 min_sensor_distance: float = 1.0):
        super().__init__(ls.getGridArea(), gridWidth, gridHeight)
        self.min_sensor_distance = min_sensor_distance
        self.ls: LightSkin = ls
        self.rayModel: RayGridInfluenceModel = ray_model
        self.rayModel.gridDefinition = self.gridDefinition

    def calculate(self, onlySelected=True) -> bool:
        """ Calculate the sensitivity values for the grid elements using the model info """
        self.grid = self.gridDefinition.makeGridFilledWith(0.0)

        m = 0.0
        """ Maximum value """

        for i_l, l in enumerate(self.ls.LEDs):
            if self.ls.selectedLED >= 0 and self.ls.selectedLED != i_l:
                continue
            for i_s, s in enumerate(self.ls.sensors):
                if self.ls.selectedSensor >= 0 and self.ls.selectedSensor != i_s:
                    continue
                ray = self.ls.getRayFromLEDToSensor(i_s, i_l)
                cells = self.rayModel.getInfluencesForRay(ray)

                for ((x, y), w) in cells:
                    if min(
                            self.gridDefinition.distanceToCell(x, y, l),
                            self.gridDefinition.distanceToCell(x, y, s)
                    ) > self.min_sensor_distance:
                        self.grid[x][y] += w
                        m = max(m, self.grid[x][y])

        # scale everything by max
        if m > 0:
            for x in range(self.gridDefinition.cellsX):
                for y in range(self.gridDefinition.cellsY):
                    self.grid[x][y] /= m

        return True
