from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import math

from Helpers.Grids import ValueGridDefinition


class Ray:
    def __init__(self, start_x: float, start_y: float, end_x: float, end_y: float):
        self.start_x: float = float(start_x)
        self.start_y: float = float(start_y)
        self.end_x: float = float(end_x)
        self.end_y: float = float(end_y)

    def __hash__(self):
        return hash((self.start_x, self.start_y, self.end_x, self.end_y))

    @property
    def length(self) -> float:
        return math.sqrt(self.dx ** 2 + self.dy ** 2)

    @property
    def dx(self) -> float:
        return self.end_x - self.start_x

    @property
    def dy(self) -> float:
        return self.end_y - self.start_y

    @property
    def eq_c(self) -> float:
        return self.end_x * self.start_y - self.start_x * self.end_y

    def distance_to_point(self, x_p: Union[float, Tuple[float, float]], y: float = 0.0) -> float:
        if isinstance(x_p, tuple):
            x: float = x_p[0]
            y: float = x_p[1]
        else:
            x: float = x_p
        return abs(self.dy * x - self.dx * y + self.eq_c) / self.length

    def closest_point_on_line(self, x_p: Union[float, Tuple[float, float]], y: float = 0.0) -> Tuple[float, float]:
        if isinstance(x_p, tuple):
            x: float = x_p[0]
            y: float = x_p[1]
        else:
            x: float = x_p

        c = self.eq_c
        len2 = (self.dx ** 2 + self.dy ** 2)
        bxay = (self.dx*x + self.dy*y)

        px = (self.dx * bxay - self.dy*c) / len2
        py = (self.dy * bxay + self.dx*c) / len2

        return px, py


class RayGridInfluenceModel(ABC):

    def __init__(self, grid_definition: ValueGridDefinition = None):
        self.gridDefinition: ValueGridDefinition = grid_definition

    def __hash__(self):
        return hash((self.__class__.__name__, self.gridDefinition))

    @abstractmethod
    def getInfluencesForRay(self, ray: Ray) -> List[Tuple[Tuple[int, int], float]]:
        """
            Returns a list of cells and their respective weights for the given ray in the current grid.

            The list should not contain duplicate cells
        """
        raise NotImplementedError("Method not yet implemented")
