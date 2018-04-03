from abc import abstractmethod

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from Helpers.ValueMap import ValueMap
from LightSkin import LightSkin


class SensitivityMap(ValueMap):
    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int,
                 ray_model: RayGridInfluenceModel):
        super().__init__(ls.getGridArea(), gridWidth, gridHeight)
        self.ls: LightSkin = ls
        self.rayModel: RayGridInfluenceModel = ray_model
        self.rayModel.gridDefinition = self.gridDefinition

    @abstractmethod
    def calculate(self) -> bool:
        """Calculate the sensitivity values for the grid elements using the model info """
        self.grid = self.gridDefinition.makeFloatGridFilledWith(0.0)

        m = 0.0
        """ Maximum value """

        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                ray = self.ls.getRayFromLEDToSensor(i_s, i_l)
                cells = self.rayModel.getInfluencesForRay(ray)

                for ((x, y), w) in cells:
                    self.grid[x][y] += w
                    m = max(m, self.grid[x][y])

        # scale everything by max
        if m > 0:
            for x in range(self.gridDefinition.cellsX):
                for y in range(self.gridDefinition.cellsY):
                    self.grid[x][y] /= m

        return True
