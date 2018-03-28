from abc import ABC
from typing import List

from Helpers.Grids import ValueGridAreaDefinition, ValueGridDefinition


class ValueMap(ABC):
    def __init__(self, gridDefinition: ValueGridAreaDefinition, gridWidth: int = None, gridHeight: int = None,
                 grid: List[List[float]] = None):

        if grid is not None:
            self.grid = grid
            self.gridWidth = len(grid)
            self.gridHeight = len(grid[0])
        else:
            self.gridWidth = gridWidth
            self.gridHeight = gridHeight

            # init grid
            self.grid: List[List[float]] = []
            for i in range(gridWidth):
                self.grid.append([0.0] * gridHeight)

        self.gridDefinition: ValueGridDefinition = ValueGridDefinition.fromGridDefinition(
            gridDefinition, self.gridWidth, self.gridHeight)

    def measureAtPoint(self, x: float, y: float) -> float:
        i, j = self.gridDefinition.getCellAtPoint(x, y)
        return max(0.0, min(1.0, self.grid[i][j]))

    pass
