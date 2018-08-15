import math
from abc import ABC
from typing import Optional, Tuple, List, Union


class ValueGridAreaDefinition(ABC):
    """ A definition for a grid area; Coordinates and width / height """

    def __init__(self, start_x: float = 0, start_y: float = 0, end_x: float = 0, end_y: float = 0):
        self.startX: float = start_x
        self.startY: float = start_y
        self.endX: float = end_x
        self.endY: float = end_y
        self.width: float = self.endX - self.startX
        self.height: float = self.endY - self.startY

    def __hash__(self):
        return hash((self.startX, self.startY, self.endX, self.endY))


class ValueGridDefinition(ValueGridAreaDefinition):
    """ A definition for a grid; Coordinates, width / height and cell numbers """
    def __init__(self, start_x: float = 0, start_y: float = 0, width: float = 0, height: float = 0,
                 cells_x: int = 0, cells_y: int = 0):
        super().__init__(start_x, start_y, width, height)
        self.cellsX: int = cells_x
        self.cellsY: int = cells_y
        self.cellWidth: float = self.width / self.cellsX
        self.cellHeight: float = self.height / self.cellsY

    def __hash__(self):
        return hash((super().__hash__(), self.cellsX, self.cellsY))

    @classmethod
    def fromGridDefinition(cls, grid: ValueGridAreaDefinition, cells_x: int,
                           cells_y: int) -> 'ValueGridDefinition':
        """ Construct a grid definition by copying from a existing GridAreaDefinition """
        return cls(grid.startX, grid.startY, grid.endX, grid.endY, cells_x, cells_y)

    def getCellAtPoint(self, x: float, y: float, borders=True) -> Optional[Tuple[int, int]]:
        """ Returns the cell containing the given coordinates.
            If borders is True, cells on the border extend 'infinitely' """
        i = self.getIatX(x, borders)
        j = self.getJatY(y, borders)
        if i is None:
            return None
        return i, j

    def getIatX(self, x: float, borders=True) -> Optional[int]:
        """ Returns the i column containing the given x coordinate.
            If borders is True, cells on the border extend 'infinitely' """
        i_t = int((x - self.startX) / self.cellWidth)
        i = max(0, min(self.cellsX - 1, i_t))
        if borders is False and (i != i_t):
            return None
        return i

    def getJatY(self, y: float, borders=True) -> Optional[int]:
        """ Returns the j row containing the given y coordinate.
            If borders is True, cells on the border extend 'infinitely' """
        j_t = int((y - self.startY) / self.cellHeight)
        j = max(0, min(self.cellsY - 1, j_t))
        if borders is False and (j != j_t):
            return None
        return j

    def getPointOfCell(self, i: int, j: int, center=True) -> Tuple[float, float]:
        """ Returns the center or top-left point of the given cell """
        x = self.getXatI(i, center)
        y = self.getYatJ(j, center)
        return x, y

    def getXatI(self, i: int, center=True) -> float:
        """ Returns the x coordinate of the center or left of the given column """
        x = self.startX + i * self.cellWidth
        if center:
            x += self.cellWidth / 2
        return x

    def getYatJ(self, j: int, center=True) -> float:
        """ Returns the y coordinate of the center or top of the given row """
        y = self.startY + j * self.cellHeight
        if center:
            y += self.cellHeight / 2
        return y

    def distanceToCell(self, i: int, j: int, point_or_x: Union[Tuple[float, float], float], y: float=0.0, center=True) -> float:
        """ Returns the euclidean distance of a given point to the center / top-left corner of the cell """
        p1 = point_or_x if type(point_or_x) is tuple else (point_or_x, y)
        p2 = self.getPointOfCell(i, j, center)
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def makeGridFilledWith(self, val: any) -> List[List[any]]:
        """ Initializes a 2D list of the dimensions of this grid with the given value.
            All rows are independent. """
        ret: List[List[any]] = []
        for i in range(self.cellsX):
            ret.append([val] * self.cellsY)
        return ret
