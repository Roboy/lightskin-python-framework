import math

import re
import serial
from LightSkin import ForwardModel, LightSkin, EventHook


class ArduinoConnectorForwardModel(ForwardModel):
    sampleDistance = 0.125

    def __init__(self, ls: LightSkin):
        super().__init__(ls)

        self.onUpdate: EventHook = EventHook()

        self._sensorValues = []
        for i in range(len(self.ls.LEDs)):
            self._sensorValues.append([])
            for j in range(len(self.ls.sensors)):
                self._sensorValues[i].append(self.ls.forwardModel.getSensorValue(j, i))

        self.ser = serial.Serial(
            port='COM3',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0)

    def _readLoop(self):
        while(True):
            line = self.ser.readline()
            match = re.match('Snapshot: ([0-9]+),([0-9]+)', line)
            if match is not None:
                leds = int(match.group(0))
                sensors = int(match.group(1))
                for

    def measureAtPoint(self, x: float, y: float, led: int = -1) -> float:
        # No measurement possible
        return 0

    def getSensorValue(self, sensor: int, led: int = -1) -> float:
        if led < 0:
            led = self.ls.selectedLED
        return self._sensorValues[led][sensor]
