from abc import ABC
from typing import List

from .Grids import ValueGridAreaDefinition, ValueGridDefinition
from .Measurable import MeasurableGrid


class ValueMap(MeasurableGrid):
    """ A grid filled with floats.
        Provides measurability to display the data. """

    def __init__(self, gridDefinition: ValueGridAreaDefinition, gridWidth: int = None, gridHeight: int = None,
                 grid: List[List[float]] = None):
        """ Constructs the grid filled with floats.
            Either uses the given grid float-list or constructs a new one
            with the given gridWidth and gridHeight filled with 0.0 """
        if grid is not None:
            self.grid = grid
            gridWidth = len(grid)
            gridHeight = len(grid[0])

        self.gridDefinition: ValueGridDefinition = ValueGridDefinition.fromGridDefinition(
            gridDefinition, gridWidth, gridHeight)

        if grid is None:
            self.grid: List[List[float]] = self.gridDefinition.makeGridFilledWith(0.0)

    def measureAtPoint(self, x: float, y: float) -> float:
        i, j = self.gridDefinition.getCellAtPoint(x, y)
        return max(0.0, min(1.0, self.grid[i][j]))

    def getGridDefinition(self) -> ValueGridDefinition:
        return self.gridDefinition
