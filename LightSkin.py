#!/usr/bin/python3


class LightSkin:
    """ Container describing the setup and status of a LightSkin """

    def __init__(self):
        """ Create a container """
        self.sensors = []
        self.LEDs = []
        self.image = None
        self.selectedSensor = -1
        self.selectedLED = -1
        self.onChange = EventHook()

    def setSelectedSensor(self, i):
        old = self.selectedSensor
        self.selectedSensor = i
        self.onChange.fire('sensor', old, i)

    def setSelectedLED(self, i):
        old = self.selectedLED
        self.selectedLED = i
        self.onChange.fire('led', old, i)


# source https://stackoverflow.com/a/1094423
class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler
