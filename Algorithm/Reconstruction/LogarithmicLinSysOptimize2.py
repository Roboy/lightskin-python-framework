import math
from typing import List, Tuple
import scipy.sparse as sparse
import scipy.optimize as optimize
import numpy as np

from Algorithm.RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from Algorithm.Reconstruction.LogarithmicLinSysOptimize import LogarithmicLinSysOptimize
from LightSkin import LightSkin, Calibration, BackwardModel


class LogarithmicLinSysOptimize2(LogarithmicLinSysOptimize):
    """ Converts the problem into a set of linear equations and solves them using standard scipy.nnls """
    def calculate(self):
        self._build_system(True)
        self._solve_system()
        self._apply_solution(True)

    def _solve_system(self):
        """ solves the system of linear equations """
        result, residual = optimize.nnls(self._lgs_A.toarray(), np.asarray(self._lgs_b))

        self._lgs_sol = result