import math
import time
from typing import List, Tuple
import scipy.sparse as sparse
import scipy.optimize as optimize
import numpy as np

from .LogarithmicLinSysOptimize import LogarithmicLinSysOptimize
from ..RayInfluenceModels.RayInfluenceModel import RayGridInfluenceModel
from ...LightSkin import LightSkin, Calibration, BackwardModel


class LogarithmicLinSysOptimize2(LogarithmicLinSysOptimize):
    """ Converts the problem into a set of linear equations and solves them using standard scipy.nnls """
    def calculate(self):
        try:
            t1 = time.perf_counter()
            self._build_system(True)
            t2 = time.perf_counter()
            self._solve_system()
            t3 = time.perf_counter()
            self._apply_solution(True)
            t4 = time.perf_counter()
            print("Times needed for reconstruction: %f %f %f" % (t2-t1, t3-t2, t4-t3))
        except Exception as e:
            print("Exception when trying to reconstruct data")
            print(e)

    def _solve_system(self):
        """ solves the system of linear equations """
        result, residual = optimize.nnls(self._lgs_A.toarray(), np.asarray(self._lgs_b))

        self._lgs_sol = result