#!/usr/bin/python3

from typing import List, Tuple, Callable, Optional
from abc import ABC, abstractmethod

import math

from Helpers.EventHook import EventHook
from Helpers.Grids import ValueGridDefinition, ValueGridAreaDefinition
from Helpers.Measurable import Measurable
from Helpers.ValueMap import ValueMap


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

    def getGridArea(self) -> ValueGridAreaDefinition:
        min_x, min_y, max_x, max_y = self._findMinMaxPos()
        return ValueGridAreaDefinition(min_x, min_y, max_x, max_y)

    def _findMinMaxPos(self):
        _min_pos_x: float = math.inf
        _min_pos_y: float = math.inf
        _max_pos_x: float = -math.inf
        _max_pos_y: float = -math.inf

        for s in self.sensors:
            _min_pos_x = min(_min_pos_x, s[0])
            _max_pos_x = max(_max_pos_x, s[0])
            _min_pos_y = min(_min_pos_y, s[1])
            _max_pos_y = max(_max_pos_y, s[1])

        for s in self.LEDs:
            _min_pos_x = min(_min_pos_x, s[0])
            _max_pos_x = max(_max_pos_x, s[0])
            _min_pos_y = min(_min_pos_y, s[1])
            _max_pos_y = max(_max_pos_y, s[1])

        return _min_pos_x, _min_pos_y, _max_pos_x, _max_pos_y


class ForwardModel(Measurable):

    def __init__(self, ls: LightSkin):
        self.ls: LightSkin = ls

    def measureAtPoint(self, x: float, y: float) -> float:
        return self.measureLEDAtPoint(x, y)

    @abstractmethod
    def measureLEDAtPoint(self, x: float, y: float, led: int = -1) -> float:
        raise NotImplementedError("Method not yet implemented")

    def getSensorValue(self, sensor: int, led: int = -1) -> float:
        s = self.ls.sensors[sensor]
        return self.measureLEDAtPoint(s[0], s[1], led)

    pass


class Calibration(ABC):
    def __init__(self, ls: LightSkin):
        self.ls: LightSkin = ls

    def calibrate(self):
        pass

    @abstractmethod
    def expectedSensorValue(self, sensor: int, led: int) -> float:
        raise NotImplementedError("Method not yet implemented")


class BackwardModel(ValueMap):

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int, calibration: Calibration):
        super().__init__(ls.getGridArea(), gridWidth, gridHeight)
        self.ls: LightSkin = ls
        self.calibration: Calibration = calibration

    @abstractmethod
    def calculate(self) -> bool:
        """Apply the backward model and calculate the expected values for the grid elements using the sensor values
        retrieved from the skins forward model """
        raise NotImplementedError("Method not yet implemented")

    pass
