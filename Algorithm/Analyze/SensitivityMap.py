from abc import abstractmethod

from Helpers.ValueMap import ValueMap
from LightSkin import LightSkin


class SensitivityMap(ValueMap):
    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int):
        super().__init__(ls.getGridArea(), gridWidth, gridHeight)
        self.ls: LightSkin = ls

    @abstractmethod
    def calculate(self) -> bool:
        """Calculate the sensitivity values for the grid elements using the model info """
        pass