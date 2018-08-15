from functools import lru_cache
from typing import Tuple, List, Dict

import math

from .RayInfluenceModel import RayGridInfluenceModel, Ray


class DirectSampledRayGridInfluenceModel(RayGridInfluenceModel):
    """
        Calculates the weights of the grid cells by sampling along the direct path of the ray
        and summing up the grid elements hit
    """

    sampleDistance = 0.125

    @lru_cache(maxsize=512)
    def getInfluencesForRay(self, ray: Ray) -> List[Tuple[Tuple[int, int], float]]:
        dx = ray.dx
        dy = ray.dy
        dist = ray.length

        dx_step = dx / dist * self.sampleDistance
        dy_step = dy / dist * self.sampleDistance
        steps = dy / dy_step if dx_step == 0 else dx / dx_step

        values: Dict[Tuple[int, int], float] = {}

        for i in range(int(steps)):
            # find corresponding grid element for this sample
            x = ray.start_x + i * dx_step
            y = ray.start_y + i * dy_step

            coords = self.gridDefinition.getCellAtPoint(x, y)
            if coords not in values:
                values[coords] = 0.0
            values[coords] += self.sampleDistance

        return list(values.items())
