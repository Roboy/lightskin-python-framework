#!/usr/bin/python3
from functools import lru_cache
from typing import List, Tuple
from abc import ABC, abstractmethod

import math

from .Algorithm.RayInfluenceModels.RayInfluenceModel import Ray
from .Helpers.EventHook import EventHook
from .Helpers.Grids import ValueGridAreaDefinition
from .Helpers.Measurable import Measurable
from .Helpers.ValueMap import ValueMap


class LightSkin:
    """ Container describing the setup and status of a LightSkin """

    def __init__(self):
        """ Create a container """
        self.sensors: List[Tuple[float, float]] = []
        """ A list of the sensor coordinates """
        self.LEDs: List[Tuple[float, float]] = []
        """ A list of the led coordinates """

        self.translucencyMap: ValueMap = None
        """ A grid of translucency values to be used as ground truth """
        self.forwardModel: ForwardModel = None
        """ The default forward model to use """
        self.backwardModel: BackwardModel = None
        """ The default backward model to use """

        self._selectedSensor: int = -1
        self._selectedLED: int = -1
        self.onChange: EventHook[[str, int, int]] = EventHook()
        """ EventHook that gets triggered when the selected Sensor, LED or other values of the skin change """

    @property
    def selectedSensor(self) -> int:
        """ The index of the currently selected sensor """
        return self._selectedSensor

    @selectedSensor.setter
    def selectedSensor(self, i: int):
        """ Change the index of the currently selected sensor; triggers onChange """
        old = self._selectedSensor
        self._selectedSensor = i
        self.onChange('sensor', old, i)

    @property
    def selectedLED(self) -> int:
        """ The index of the currently selected led """
        return self._selectedLED

    @selectedLED.setter
    def selectedLED(self, i: int):
        """ Change the index of the currently selected led; triggers onChange """
        old = self._selectedLED
        self._selectedLED = i
        self.onChange('led', old, i)

    def getGridArea(self) -> ValueGridAreaDefinition:
        """ Returns the default area definition for the setup; spans all sensors and LEDs """
        min_x, min_y, max_x, max_y = self._findMinMaxPos()
        return ValueGridAreaDefinition(min_x, min_y, max_x, max_y)

    @lru_cache(maxsize=None)
    def getRayFromLEDToSensor(self, sensor: int, led: int) -> Ray:
        """ Returns the Ray from the given LED to the given sensor """
        l_x, l_y = self.LEDs[led]
        s_x, s_y = self.sensors[sensor]
        return Ray(l_x, l_y, s_x, s_y)

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
    """ A model that provides the sensor values for the current setup.
        eg. simulated values or real values from a prototype
    """

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
    """ A calibration defining the expected sensor value when no pressure is applied """
    def __init__(self, ls: LightSkin):
        self.ls: LightSkin = ls

    def current_hash(self):
        return self.__hash__()

    def calibrate(self):
        pass

    @abstractmethod
    def expectedSensorValue(self, sensor: int, led: int) -> float:
        raise NotImplementedError("Method not yet implemented")


class BackwardModel(ValueMap):
    """ An algorithm that provides functionality to reconstruct the translucency map given the skin and a calibration. """

    def __init__(self, ls: LightSkin, gridWidth: int, gridHeight: int, calibration: Calibration):
        super().__init__(ls.getGridArea(), gridWidth, gridHeight)
        self.ls: LightSkin = ls
        self.calibration: Calibration = calibration

    @abstractmethod
    def calculate(self) -> bool:
        """ Apply the backward model and calculate the expected values for the grid elements using the sensor values
        retrieved from the skins forward model """
        raise NotImplementedError("Method not yet implemented")

    pass
