from abc import ABC, abstractmethod
from typing import List, Tuple

from Helpers.Grids import ValueGridDefinition
from LightSkin import LightSkin


class RayGridInfluenceModel(ABC):

    def __init__(self, grid_definition: ValueGridDefinition):
        self.gridDefinition: ValueGridDefinition = grid_definition

    @abstractmethod
    def getInfluencesForRay(self, start_x: float, start_y: float, end_x: float, end_y: float) \
            -> List[Tuple[Tuple[int, int], float]]:
        raise NotImplementedError("Method not yet implemented")
