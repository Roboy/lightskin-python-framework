from typing import List, Tuple

from Algorithm.Reconstruction.SimpleRepeatedBackProjection import SimpleRepeatedBackProjection


class SimpleRepeatedDistributeBackProjection(SimpleRepeatedBackProjection):

    def _backProject(self, sensor: int, led: int, factor: float):
        ray = self.ls.getRayFromLEDToSensor(sensor, led)

        cells = self.rayModel.getInfluencesForRay(ray)

        dfactor = factor ** (1 / ray.length)

        alreadyDistributedFactor = dfactor
        restFactor = 1.0
        """ Factor that still needs to be distributed """
        redistributors: List[Tuple[Tuple[int, int], float]] = []
        """ Cells that can still take more factor """

        for (i, j), w in cells:
            f = dfactor
            if self._bufGrid[i][j] * dfactor > 1:  # max out at 1; cell can't take anymore
                f = 1 / self._bufGrid[i][j]  # actually just propose a factor that makes this 1
                restFactor *= (dfactor / f) ** w  # 'add up' the rest factor that still needs to be distributed
                print("didnt fit %f" % restFactor)
            else:
                # add cell to list of cells that could potentially still take more factor
                redistributors.append(((i, j), w))
            # weighted factorization
            self._tmpGrid[i][j] += f * w
            self._tmpGridWeights[i][j] += w

        while not (0.9999 < restFactor < 1.0001) and len(redistributors) > 0:
            print('Still got stuff to distribute %f into %i' % (restFactor, len(redistributors)))

            cells = redistributors
            redistributors = []
            weightSum = sum(map(lambda el: el[1], cells))

            dfactor = restFactor ** (1 / weightSum)
            alreadyDistributedFactor *= dfactor
            restFactor = 1.0

            for (i, j), w in cells:
                f = dfactor
                if self._bufGrid[i][j] * alreadyDistributedFactor > 1:  # max out at 1; cell can't take anymore
                    f = 1 / self._bufGrid[i][j]  # actually just propose a factor that makes this 1
                    restFactor *= (dfactor / f) ** w  # 'add up' the rest factor that still needs to be distributed
                else:
                    # add cell to list of cells that could potentially still take more factor
                    redistributors.append(((i, j), w))
                # weighted factorization
                self._tmpGrid[i][j] += f * w
