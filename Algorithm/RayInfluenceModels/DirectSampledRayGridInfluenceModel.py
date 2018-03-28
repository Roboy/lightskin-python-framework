from typing import Tuple, List

import math

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel


class DirectSampledRayGridInfluenceModel(RayGridInfluenceModel):
    """
        Calculates the weights of the grid cells by sampling along the direct path of the ray
        and summing up the grid elements hit
    """

    sampleDistance = 0.125

    def getInfluencesForRay(self, start_x: float, start_y: float, end_x: float, end_y: float) \
            -> List[Tuple[Tuple[int, int], float]]:
        dx = float(end_x - start_x)
        dy = float(end_y - start_y)

        dist = math.sqrt(dx ** 2 + dy ** 2)

        dx_step = dx / dist * self.sampleDistance
        dy_step = dy / dist * self.sampleDistance
        steps = dy / dy_step if dx_step == 0 else dx / dx_step

        values = {}

        for i in range(int(steps)):
            # find corresponding grid element for this sample
            x = start_x + i * dx_step
            y = start_y + i * dy_step

            coords = self.gridDefinition.getCellAtPoint(x, y)
            if coords not in values:
                values[coords] = 0.0
            values[coords] += self.sampleDistance

        return list(values.items())
