from functools import lru_cache
from typing import Tuple, List, Dict

import math

from .RayInfluenceModel import RayGridInfluenceModel, Ray


class WideRayGridInfluenceModel(RayGridInfluenceModel):
    """
        Calculates the weights of the grid cells by calculating the distance of the center of the cell to the ray.
    """

    max_distance = 1.0

    @lru_cache(maxsize=512)
    def getInfluencesForRay(self, ray: Ray) -> List[Tuple[Tuple[int, int], float]]:

        # find relevant x coordinates
        start_x = ray.start_x
        end_x = ray.end_x
        if ray.dx < 0:
            start_x += self.max_distance
            end_x -= self.max_distance
        else:
            start_x -= self.max_distance
            end_x += self.max_distance

        start_i = self.gridDefinition.getIatX(start_x)
        end_i = self.gridDefinition.getIatX(end_x)

        values: List[Tuple[Tuple[int, int], float]] = []

        c = ray.c

        # direction in which to count
        idir = int(math.copysign(1, end_i-start_i))

        # including end
        for i in range(start_i, end_i+idir, idir):

            x = self.gridDefinition.getXatI(i)

            start_y = self.gridDefinition.startY
            end_y = self.gridDefinition.endY
            if abs(ray.dx) > 0:
                start_y = max(
                    self.gridDefinition.startY, min(
                        self.gridDefinition.endY,
                        (self.max_distance * ray.length - c - ray.dy*x) / -ray.dx))
                end_y = max(
                    self.gridDefinition.startY, min(
                        self.gridDefinition.endY,
                        (- self.max_distance * ray.length - c - ray.dy*x) / -ray.dx))

            start_j = self.gridDefinition.getJatY(start_y)
            end_j = self.gridDefinition.getJatY(end_y)

            jdir = int(math.copysign(1, end_j-start_j))
            for j in range(start_j, end_j+jdir, jdir):
                y = self.gridDefinition.getYatJ(j)
                p = ray.closest_point_on_line(x, y)
                dx = abs(p[0]-x)
                dy = abs(p[1]-y)
                dl = ray.distance_of_point_along_ray(p, relative=True)
                # limit ray to from LED to sensor
                if not 0 < dl < 1:
                    continue
                influence = self.getInfluenceFromDistance(dx, dy, dl, ray)
                values.append(((i, j), influence))

        return values

    def getInfluenceFromDistance(self, dx: float, dy: float, dl: float, ray: Ray) -> float:
        """
            Returns the influence of a cell given the minimal distance to the direct ray
            dx and dy as separate parameters so possible non-square grids can be handled
            (if the grid-size is relevant to the influence function)
            :param dx: x distance to ray
            :param dy: y distance to ray
            :param dl: position along the ray; 0.0 = led; 1.0 = sensor
            :param ray: the ray currently in question
            :return: intensity
        """
        return 1/(1 + 0.1 * ((dx**2 + dy**2)*100)**1.5) / ray.length
