from abc import ABC, abstractmethod
from typing import List, Tuple

from LightSkin import LightSkin


class RayInfluenceGridModel(ABC):

    def __init__(self, ls: LightSkin):
        self.ls: LightSkin = ls

        self.gridWidth = 0
        self.gridHeight = 0
        self.gridStartX = 0
        self.gridStartY = 0
        self.gridCellWidth = 0
        self.gridCellHeight = 0

    @abstractmethod
    def getInfluencesForRay(self, startX:float, startY:float, endX:float, endY:float)\
            -> List[Tuple[float, Tuple[int, int]]]:
        pass
