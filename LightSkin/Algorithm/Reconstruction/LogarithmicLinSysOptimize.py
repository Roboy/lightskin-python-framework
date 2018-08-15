import math
import time
from typing import List, Tuple
import scipy.sparse as sparse
import scipy.optimize as optimize
import numpy as np

from ..RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from ...LightSkin import LightSkin, Calibration, BackwardModel


class LogarithmicLinSysOptimize(BackwardModel):
    """ Converts the problem into a set of linear equations and solves them using standard libraries """
    MIN_SENSITIVITY = 0.02
    _MIN_TRANSLUCENCY = 0.000001
    """ Minimal translucency is relevant in log space so we don't get -inf as values """

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

        self._construct_hash = None
        self._lgs_A: sparse.csr_matrix = None
        self._lgs_b: List[float] = []
        self._lgs_sol: List[float] = []

    def calculate(self):
        try:
            t1 = time.perf_counter()
            self._build_system()
            t2 = time.perf_counter()
            self._solve_system()
            t3 = time.perf_counter()
            self._apply_solution()
            t4 = time.perf_counter()
            print("Times needed for reconstruction: %f %f %f" % (t2 - t1, t3 - t2, t4 - t3))
        except Exception as e:
            print("Exception when trying to reconstruct data")
            print(e)

    def _build_system(self, positive=False, force_full_build=False):
        """ Builds the system of linear equations from rays and sensor data """
        # Number of rows in the matrix; every ray (LEDs x Sensors) is one equation
        m = len(self.ls.LEDs) * len(self.ls.sensors)
        # Number of columns: the variables we are searching
        n = self.gridDefinition.cellsX * self.gridDefinition.cellsY

        c_hash = hash((m, n, self.calibration, self.rayModel))
        if self._construct_hash != c_hash:
            force_full_build = True
        self._construct_hash = c_hash

        self._lgs_b = []
        rows: List[sparse.csr_matrix] = []

        # Build matrix row by row and b vector
        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                expected_val = self.calibration.expectedSensorValue(i_s, i_l)
                if expected_val > self.MIN_SENSITIVITY:
                    val = max(self._MIN_TRANSLUCENCY, self.ls.forwardModel.getSensorValue(i_s, i_l))
                    translucency = math.log(val / expected_val)\
                        if expected_val > self.MIN_SENSITIVITY else 0.0
                    translucency = min(translucency, -0.0)  # make sure we are in a valid area
                    if positive:
                        translucency = abs(translucency)

                    # Expected result into b-vector
                    self._lgs_b.append(translucency)

                    if force_full_build:
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

                        row = sparse.csr_matrix((data, col_ind, [0, len(data)]), shape=(1, n))
                        rows.append(row)

        if force_full_build:
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
