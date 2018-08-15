from typing import List, Tuple

from .SimpleRepeatedBackProjection import SimpleRepeatedBackProjection


class SimpleRepeatedDistributeBackProjection(SimpleRepeatedBackProjection):
    """ Slight improvement on the repeated back projection:
        When projecting back the error, no cell can have a factor above 1.
        Instead of discarding the value when this happens, it is further distributed onto all cells.
        This speeds up the converging of the result.
    """

    def _backProject(self, sensor: int, led: int, factor: float):
        ray = self.ls.getRayFromLEDToSensor(sensor, led)

        cells = self.rayModel.getInfluencesForRay(ray)
        """ cells that are open for the next round """

        rest_factor = factor
        """ Factor that still needs to be distributed """
        dfactor = 1.0
        """ Factor per distance in the current iteration; factor currently applied to all cells that are left """
        cells_left: List[Tuple[Tuple[int, int], float]] = []
        """ Cells that can still take more factor """
        cells_finished: List[Tuple[Tuple[int, int], float, float]] = []
        """ Cells for which the resulting factor has already been calculated """

        #print('Distributing %f into %i' % (rest_factor, len(cells)))
        while (abs(1 - rest_factor) > .000001) and len(cells) > 0:
            # While there is still factor to be distributed and we still have cells that can take factor

            weight_sum = sum(map(lambda el: el[1], cells))
            total_factor = rest_factor * (dfactor ** weight_sum)
            """ total factor left =
                rest_factor needed to be applied + factor currently applied on all cells that are still open
            """
            dfactor = total_factor ** (1 / weight_sum)
            rest_factor = 1.0

            for (i, j), w in cells:
                if self._bufGrid[i][j] * dfactor > 1:  # max out at 1; cell can't take anymore
                    #print('Doesnt fit cell %f %f' % (self._bufGrid[i][j] * dfactor, dfactor))
                    f = 1 / self._bufGrid[i][j]
                    # f is the maximum the cell can still take
                    rest_factor *= (dfactor / f) ** w
                    # 'add up' to the rest factor that still needs to be distributed
                    cells_finished.append(((i, j), w, f))
                    # The resulting factor for this cell has been determined; no more work needed
                else:
                    # add cell to list of cells that could potentially still take more factor
                    cells_left.append(((i, j), w))

            cells = cells_left
            cells_left = []
            #print('Still got stuff to distribute %f into %i' % (rest_factor, len(cells)))

        # all remaining cells get the current dfactor
        for (i, j), w in cells:
            cells_finished.append(((i, j), w, dfactor))

        for (i, j), w, f in cells_finished:
            self._tmpGrid[i][j] += f * w
            self._tmpGridWeights[i][j] += w
