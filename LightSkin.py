#!/usr/bin/python3

from typing import List, Tuple, Callable
from abc import ABC, abstractmethod


class LightSkin:
    """ Container describing the setup and status of a LightSkin """

    def __init__(self):
        """ Create a container """
        self.sensors: List[Tuple[float, float]] = []
        self.LEDs: List[Tuple[float, float]] = []
        self.image = None
        self._selectedSensor: int = -1
        self._selectedLED: int = -1
        self.onChange: EventHook[[str, int, int]] = EventHook()
        self.forwardModel: ForwardModel = None

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
