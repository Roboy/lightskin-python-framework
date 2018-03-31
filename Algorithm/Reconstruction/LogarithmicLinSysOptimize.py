import math
from typing import List, Tuple
import scipy.sparse as sparse
import scipy.optimize as optimize
import numpy as np

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from LightSkin import LightSkin, Calibration, BackwardModel


class LogarithmicLinSysOptimize(BackwardModel):
    """ Converts the problem into a set of linear equations and solves them using standard libraries """
    MIN_SENSITIVITY = 0.02

    def __init__(self, ls: LightSkin,
                 gridWidth: int,
                 gridHeight: int,
                 calibration: Calibration,
                 ray_model: RayGridInfluenceModel):
        super().__init__(ls, gridWidth, gridHeight, calibration)
        self._tmpGrid = []
        self._tmpGridWeights = []
        self._bufGrid: List[List[float]] = []
        self.rayModel: RayGridInfluenceModel = ray_model
        self.rayModel.gridDefinition = self.gridDefinition
        """ Contains the weights while they are being built in log space """

        self._lgs_A: sparse.csr_matrix = None
        self._lgs_b: List[float] = []

    def calculate(self):
        # Number of rows in the matrix; every ray (LEDs x Sensors) is one equation
        m = len(self.ls.LEDs) * len(self.ls.sensors)
        # Number of columns: the variables we are searching
        n = self.gridDefinition.cellsX * self.gridDefinition.cellsY

        self._lgs_b = []
        rows: List[sparse.csr_matrix] = []

        # Build matrix row by row and b vector
        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                expected_val = self.calibration.expectedSensorValue(i_s, i_l)
                if expected_val > self.MIN_SENSITIVITY:
                    val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                    translucency = math.log(val / expected_val) if expected_val > self.MIN_SENSITIVITY else 0.0

                    # Expected result into b-vector
                    self._lgs_b.append(translucency)

                    # build sparse row
                    ray = self.ls.getRayFromLEDToSensor(i_s, i_l)
                    cells = self.rayModel.getInfluencesForRay(ray)

                    data: List[float] = [0.0] * len(cells)
                    col_ind: List[int] = [0] * len(cells)
                    for i, ((x, y), w) in enumerate(cells):
                        data[i] = w
                        col_ind[i] = y * self.gridDefinition.cellsX + x
                        # if x == 0 and y == 0:
                        #     print("in matr w %i weight for %i (%i %i) %f" % (n, col_ind[i], x, y, w))

                    row = sparse.csr_matrix((data, ([0] * len(cells), col_ind)), shape=(1, n))
                    rows.append(row)

        self._lgs_A = sparse.vstack(rows)

        # Start solving

        result = optimize.lsq_linear(self._lgs_A, self._lgs_b, (-np.inf, 0), verbose=0)

        # Set solution as grid values

        if not result.success:
            print("No good solution found!")

        solution = result.x
        for i, v in enumerate(solution):
            y, x = divmod(i, self.gridDefinition.cellsX)
            value = math.exp(v)
            #if x == 0 and y == 0:
            #   print("setting val %i %i to %f (%f)" % (x, y, value, v))
            self.grid[x][y] = value
