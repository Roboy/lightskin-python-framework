from abc import ABC, abstractmethod

from .Grids import ValueGridDefinition


class Measurable(ABC):
    """ A class that can be measured at a given point to return a float """

    @abstractmethod
    def measureAtPoint(self, x: float, y: float) -> float:
        raise NotImplementedError("Method not yet implemented")


class MeasurableGrid(Measurable):

    @abstractmethod
    def getGridDefinition(self) -> ValueGridDefinition:
        raise NotImplementedError("Method not yet implemented")
