import math

from LightSkin import ForwardModel


class ArduinoConnectorForwardModel(ForwardModel):
    sampleDistance = 0.125

    def measureAtPoint(self, x: float, y: float, led: int = -1) -> float:
        # No measurement possible
        return 0

    def getSensorValue(self, sensor: int, led: int = -1) -> float:
        return 1
