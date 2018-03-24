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
            self._sensorValues.append([1.0] * len(self.ls.sensors))

        self.ser = serial.Serial(
            port='COM3',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=10)

    def _readLoop(self):
        while True:
            line = self.ser.readline()
            match = re.match('Snapshot: ([0-9]+),([0-9]+)', line)
            if match is not None:
                leds = int(match.group(0))
                sensors = int(match.group(1))
                if leds != len(self.ls.LEDs) or sensors != len(self.ls.sensors):
                    print("Received wring amount of sensor values: %i / %i; expected %i / %i" % (
                    leds, sensors, len(self.ls.LEDs), len(self.ls.sensors)))
                else:
                    for l in range(leds):
                        line = self.ser.readline()
                        vals = line.split(',')
                        for s in range(sensors):
                            self._sensorValues[l][s] = float(vals[s]) if s < len(vals) else 0.0
                    print("received data")

    def measureAtPoint(self, x: float, y: float, led: int = -1) -> float:
        # No measurement possible
        return 0.0

    def getSensorValue(self, sensor: int, led: int = -1) -> float:
        if led < 0:
            led = self.ls.selectedLED
        return self._sensorValues[led][sensor]
