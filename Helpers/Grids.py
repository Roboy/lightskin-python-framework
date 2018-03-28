from abc import ABC
from typing import Optional, Tuple


class ValueGridAreaDefinition(ABC):
    def __init__(self, start_x: float = 0, start_y: float = 0, end_x: float = 0, end_y: float = 0):
        self.startX: float = start_x
        self.startY: float = start_y
        self.endX: float = end_x
        self.endY: float = end_y
        self.width: float = self.endX - self.startX
        self.height: float = self.endY - self.startY


class ValueGridDefinition(ValueGridAreaDefinition):
    def __init__(self, start_x: float = 0, start_y: float = 0, width: float = 0, height: float = 0,
                 cells_x: int = 0, cells_y: int = 0):
        super().__init__(start_x, start_y, width, height)
        self.cellsX: int = cells_x
        self.cellsY: int = cells_y
        self.cellWidth: float = self.width / self.cellsX
        self.cellHeight: float = self.height / self.cellsY

    @classmethod
    def createFromGridDefinition(cls, grid: ValueGridAreaDefinition, cells_x: int,
                                 cells_y: int) -> ValueGridAreaDefinition:
        return cls(grid.startX, grid.startY, grid.endX, grid.endY, cells_x, cells_y)

    def getCellAtPoint(self, x: float, y: float, borders=True) -> Optional[Tuple[int, int]]:
        i_t = int((x - self.startX) / self.cellWidth)
        j_t = int((y - self.startY) / self.cellHeight)

        i = max(0, min(self.cellsX - 1, i_t))
        j = max(0, min(self.cellsY - 1, j_t))

        if borders is False and (i != i_t or j != j_t):
            return None

        return i, j
