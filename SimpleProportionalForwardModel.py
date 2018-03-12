import math

from LightSkin import ForwardModel


class SimpleProportionalForwardModel(ForwardModel):
    def measureAtPoint(self, x: float, y: float, led: int = -1) -> float:
        LED = self.ls.LEDs[led if led >= 0 else self.ls.selectedLED]
        dist = math.sqrt((x - LED[0]) ** 2 + (y - LED[0]) ** 2)

        #print("Calculated value for LED %i (%i, %i) to (%i, %i) Distance: %i" % (led, LED[0], LED[1], x, y, dist))
        return max(0.0, min(1.0, 5 / dist))
