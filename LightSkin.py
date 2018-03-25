#!/usr/bin/python3

from typing import List, Tuple, Callable
from abc import ABC, abstractmethod

import math


class LightSkin:
    """ Container describing the setup and status of a LightSkin """

    def __init__(self):
        """ Create a container """
        self.sensors: List[Tuple[float, float]] = []
        self.LEDs: List[Tuple[float, float]] = []

        self.translucencyMap: ValueMap = None
        self.forwardModel: ForwardModel = None
        self.backwardModel: BackwardModel = None

        self._selectedSensor: int = -1
        self._selectedLED: int = -1
        self.onChange: EventHook[[str, int, int]] = EventHook()

    @property
    def selectedSensor(self) -> int:
        return self._selectedSensor

    @selectedSensor.setter
    def selectedSensor(self, i: int):
        old = self._selectedSensor
        self._selectedSensor = i
        self.onChange.fire('sensor', old, i)

    @property
    def selectedLED(self) -> int:
        return self._selectedLED

    @selectedLED.setter
    def selectedLED(self, i: int):
        old = self._selectedLED
        self._selectedLED = i
        self.onChange.fire('led', old, i)


class ValueMap(ABC):
    def __init__(self, gridWidth: int=None, gridHeight: int=None, grid: List[List[float]]=None):

        if grid is not None:
            self.grid = grid
            self.gridWidth = len(grid)
            self.gridHeight = len(grid[0])
        else:
            self.gridWidth = gridWidth
            self.gridHeight = gridHeight

            # init grid
            self.grid: List[List[float]] = []
            for i in range(gridWidth):
                self.grid.append([0.0] * gridHeight)

        self._min_pos_x: float = 0.0
        self._min_pos_y: float = 0.0
        self._rect_w: float = 0.0
        self._rect_h: float = 0.0

    def measureAtPoint(self, x: float, y: float) -> float:
        i = int((x - self._min_pos_x) / self._rect_w)
        j = int((y - self._min_pos_y) / self._rect_h)

        i = max(0, min(self.gridWidth-1, i))
        j = max(0, min(self.gridHeight-1, j))

        return max(0.0, min(1.0, self.grid[i][j]))

    pass


class LSValueMap(ValueMap):

    def __init__(self, ls: LightSkin, gridWidth: int=None, gridHeight: int=None, grid: List[List[float]]=None):
        super().__init__(gridWidth, gridHeight, grid)
        self.ls: LightSkin = ls

        self._initMinMax()

    def _initMinMax(self):
        self._min_pos_x: float = math.inf
        self._min_pos_y: float = math.inf
        self._max_pos_x: float = -math.inf
        self._max_pos_y: float = -math.inf

        for s in self.ls.sensors:
            self._min_pos_x = min(self._min_pos_x, s[0])
            self._max_pos_x = max(self._max_pos_x, s[0])
            self._min_pos_y = min(self._min_pos_y, s[1])
            self._max_pos_y = max(self._max_pos_y, s[1])

        for s in self.ls.LEDs:
            self._min_pos_x = min(self._min_pos_x, s[0])
            self._max_pos_x = max(self._max_pos_x, s[0])
            self._min_pos_y = min(self._min_pos_y, s[1])
            self._max_pos_y = max(self._max_pos_y, s[1])

        self._rect_w: float = float(self._max_pos_x - self._min_pos_x) / self.gridWidth
        self._rect_h: float = float(self._max_pos_y - self._min_pos_y) / self.gridHeight


class ForwardModel(ABC):

    def __init__(self, ls: LightSkin):
        self.ls: LightSkin = ls

    @abstractmethod
    def measureAtPoint(self, x: float, y: float, led: int = -1) -> float:
        pass

    def getSensorValue(self, sensor: int, led: int = -1) -> float:
        s = self.ls.sensors[sensor]
        return self.measureAtPoint(s[0], s[1], led)

    pass


class Calibration(ABC):
    def __init__(self, ls: LightSkin):
        self.ls: LightSkin = ls

    def calibrate(self):
        pass

    @abstractmethod
    def expectedSensorValue(self, sensor: int, led: int) -> float:
        return 0.0


class BackwardModel(LSValueMap):

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int, calibration: Calibration):
        super().__init__(ls, gridWidth, gridHeight)
        self.calibration: Calibration = calibration

    @abstractmethod
    def calculate(self) -> bool:
        """Apply the backward model and calculate the expected values for the grid elements using the sensor values
        retrieved from the skins forward model """
        pass

    pass


# source https://stackoverflow.com/a/1094423
class EventHook:

    def __init__(self):
        self.__handlers: List[Callable] = []

    def __iadd__(self, handler: Callable):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler: Callable):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler
