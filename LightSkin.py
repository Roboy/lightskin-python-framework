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
