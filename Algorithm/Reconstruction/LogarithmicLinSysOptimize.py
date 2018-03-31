import math
from typing import List, Tuple
import scipy.sparse as sparse

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from LightSkin import LightSkin, Calibration, BackwardModel


class LogarithmicLinSysOptimize(BackwardModel):
    """ Converts the problem into a set of linear equations and solves them using standard libraries """
    MIN_SENSITIVITY = 0.02
    UNKNOWN_VAL = 0.0

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

        self.sparse_matrix: sparse.csr_matrix = None

    def calculate(self):
        # Number of rows in the matrix; every ray (LEDs x Sensors) is one equation
        sensornum = len(self.ls.sensors)
        m = len(self.ls.LEDs) * sensornum
        # Number of columns: the variables we are searching
        n = self.gridDefinition.cellsX * self.gridDefinition.cellsY

        b = [0.0] * m
        rows: List[sparse.csr_matrix] = []

        # Build matrix row by row and b vector
        for i_l, l in enumerate(self.ls.LEDs):
            for i_s, s in enumerate(self.ls.sensors):
                expected_val = self.calibration.expectedSensorValue(i_s, i_l)
                if expected_val > self.MIN_SENSITIVITY:
                    val = self.ls.forwardModel.getSensorValue(i_s, i_l)
                    translucency = math.log(val / expected_val)

                    # Expected result into b-vector
                    b[i_l * sensornum + i_s] = translucency

                    # build sparse row
                    ray = self.ls.getRayFromLEDToSensor(i_s, i_l)
                    cells = self.rayModel.getInfluencesForRay(ray)

                    data: List[float] = [0.0] * len(cells)
                    col_ind: List[int] = [0] * len(cells)
                    for i, ((x, y), w) in enumerate(cells):
                        data[i] = w
                        col_ind[i] = y * self.gridDefinition.cellsX + x
                        #print("in matr w %i weight for %i (%i %i) %f" % (n, col_ind[i], x, y, w))

                    row = sparse.csr_matrix((data, ([0] * len(cells), col_ind)), shape=(1, n))
                    rows.append(row)

        self.sparse_matrix = sparse.vstack(rows)
