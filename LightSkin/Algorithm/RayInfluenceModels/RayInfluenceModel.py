from abc import ABC, abstractmethod
from typing import List, Tuple, Union

import math

from ...Helpers.Grids import ValueGridDefinition


class Ray:
    """ A Ray from a given point to another on the cartesian coordinate system. """

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
    def c(self) -> float:
        """ The c parameter where the linear equation `dy * x + dx * y + c = 0` describes this ray """
        return self.end_x * self.start_y - self.start_x * self.end_y

    def point_along_ray(self, d: float, relative=False) -> Tuple[float, float]:
        """ Returns the point that is the given distance along the ray """
        if not relative:
            d /= self.length
        x = self.start_x + d * self.dx
        y = self.start_y + d * self.dy
        return x, y

    def distance_of_point_along_ray(self, x_p: Union[float, Tuple[float, float]], y: float = 0.0, relative=False) -> float:
        """ Returns the distance that the given point lies on along the ray; perpendicular distance is ignored """
        if isinstance(x_p, tuple):
            x: float = x_p[0]
            y: float = x_p[1]
        else:
            x: float = x_p
        x -= self.start_x
        y -= self.start_y
        if relative:
            x /= self.length
            y /= self.length
        return (self.dx * x + self.dy * y) / self.length

    def distance_to_point(self, x_p: Union[float, Tuple[float, float]], y: float = 0.0) -> float:
        """ Returns the shortest distance from the given point to the infinite line defined by this ray """
        if isinstance(x_p, tuple):
            x: float = x_p[0]
            y: float = x_p[1]
        else:
            x: float = x_p
        return abs(self.dy * x - self.dx * y + self.c) / self.length

    def closest_point_on_line(self, x_p: Union[float, Tuple[float, float]], y: float = 0.0) -> Tuple[float, float]:
        """ Returns the closest point to the given point that lies on the infinite line defined by this ray """
        if isinstance(x_p, tuple):
            x: float = x_p[0]
            y: float = x_p[1]
        else:
            x: float = x_p

        # cache re-used vars
        c = self.c
        len2 = (self.dx ** 2 + self.dy ** 2)
        bxay = (self.dx*x + self.dy*y)

        px = (self.dx * bxay - self.dy*c) / len2
        py = (self.dy * bxay + self.dx*c) / len2

        return px, py


class RayGridInfluenceModel(ABC):
    """ A model describing how much influence cells of the given grid have on a given ray. """

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
