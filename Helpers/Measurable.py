from abc import ABC, abstractmethod

from Helpers.Grids import ValueGridDefinition


class Measurable(ABC):

    @abstractmethod
    def measureAtPoint(self, x: float, y: float) -> float:
        raise NotImplementedError("Method not yet implemented")


class MeasurableGrid(Measurable):

    @abstractmethod
    def getGridDefinition(self) -> ValueGridDefinition:
        raise NotImplementedError("Method not yet implemented")
