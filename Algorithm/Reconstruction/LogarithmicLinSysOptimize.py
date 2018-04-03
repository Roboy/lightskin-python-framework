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
        self._lgs_sol: List[float] = []

    def calculate(self):
        self._build_system()
        self._solve_system()
        self._apply_solution()


    def _build_system(self, positive=False):
        """ Builds the system of linear equations from rays and sensor data """
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
                    translucency = min(translucency, -0.0)  # make sure we are in a valid area
                    if positive:
                        translucency = -translucency

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

    def _solve_system(self):
        """ solves the system of linear equations """
        result = optimize.lsq_linear(self._lgs_A, self._lgs_b, (-np.inf, 0), verbose=0)

        if not result.success:
            print("No good solution found!")

        self._lgs_sol = result.x

    def _apply_solution(self, positive=False):
        """ applies the solution of the system to the grid """

        for i, v in enumerate(self._lgs_sol):
            y, x = divmod(i, self.gridDefinition.cellsX)
            value = math.exp(-v if positive else v)
            # if x == 0 and y == 0:
            #   print("setting val %i %i to %f (%f)" % (x, y, value, v))
            self.grid[x][y] = value