from functools import lru_cache
from typing import Tuple, List, Dict

import math

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel, Ray


class WideRayGridInfluenceModel(RayGridInfluenceModel):
    """
        Calculates the weights of the grid cells by calculating the distance of the center of the cell to the ray.
    """

    max_distance = 1.0

    @lru_cache(maxsize=512)
    def getInfluencesForRay(self, ray: Ray) -> List[Tuple[Tuple[int, int], float]]:

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

        c = ray.eq_c

        print('RayX: %f - %f' % (ray.start_x, ray.end_x))
        print('X: %f - %f' % (start_x, end_x))
        print('I: %i - %i' % (start_i, end_i))

        for i in range(start_i, end_i, int(math.copysign(1, end_i-start_i))):
            print('I: %i' % i)

            x = self.gridDefinition.getXatI(i)

            start_y = (self.max_distance * ray.length - c - ray.dy*x) / -ray.dx
            end_y = (- self.max_distance * ray.length - c - ray.dy*x) / -ray.dx

            start_j = self.gridDefinition.getJatY(start_y)
            end_j = self.gridDefinition.getJatY(end_y)

            print('X Y: %f, %f - %f' % (x, start_y, end_y))
            print('J: %i - %i' % (start_j, end_j))

            for j in range(start_j, end_j, int(math.copysign(1, end_j-start_j))):
                p = self.gridDefinition.getPointOfCell(i, j)
                p2 = ray.closest_point_on_line(p)
                dx = abs(p2[0]-p[0])
                dy = abs(p2[1]-p[1])
                influence = self.getInfluenceFromDistance(dx, dy)

                print('Cell has Influence: %i %i : %f %f : %f' % (i, j, p2[0], p2[1], influence))
                values.append(((i, j), influence))

        return values

    def getInfluenceFromDistance(self, dx: float, dy: float) -> float:
        """
            dx and dy as separate parameters so possible non-square grids can be handled
            (if the grid-size is relevant to the influence function)
            :param dx:
            :param dy:
            :return:
        """
        return math.sqrt(dx**2 + dy**2)
