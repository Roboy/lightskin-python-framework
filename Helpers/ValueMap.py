from abc import ABC
from typing import List

from Helpers.Grids import ValueGridAreaDefinition, ValueGridDefinition
from Helpers.Measurable import MeasurableGrid


class ValueMap(MeasurableGrid):
    def __init__(self, gridDefinition: ValueGridAreaDefinition, gridWidth: int = None, gridHeight: int = None,
                 grid: List[List[float]] = None):

        if grid is not None:
            self.grid = grid
            gridWidth = len(grid)
            gridHeight = len(grid[0])
        else:
            # init grid
            self.grid: List[List[float]] = []
            for i in range(gridWidth):
                self.grid.append([0.0] * gridHeight)

        self.gridDefinition: ValueGridDefinition = ValueGridDefinition.fromGridDefinition(
            gridDefinition, gridWidth, gridHeight)

    def measureAtPoint(self, x: float, y: float) -> float:
        i, j = self.gridDefinition.getCellAtPoint(x, y)
        return max(0.0, min(1.0, self.grid[i][j]))

    def getGridDefinition(self) -> ValueGridDefinition:
        return self.gridDefinition
