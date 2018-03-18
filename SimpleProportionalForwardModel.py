import math

from LightSkin import ForwardModel


class SimpleProportionalForwardModel(ForwardModel):
    sampleDistance = 0.25

    def measureAtPoint(self, x: float, y: float, led: int = -1) -> float:
        LED = self.ls.LEDs[led if led >= 0 else self.ls.selectedLED]

        dx = float(x - LED[0])
        dy = float(y - LED[1])

        dist = math.sqrt(dx ** 2 + dy ** 2)
        translucencyMul = 1

        if dist > 0:
            # sample translucency map
            dxStep = dx / dist * self.sampleDistance
            dyStep = dy / dist * self.sampleDistance
            steps = dy/dyStep if dxStep == 0 else dx/dxStep
            #print("Sampling for LED %i with %i steps" % (led, steps))
            for i in range(int(steps)):
                translucencyMul *= self.ls.translucencyMap.measureAtPoint(LED[0]+i*dxStep, LED[1]+i*dyStep)\
                                   ** self.sampleDistance

        dist = max(dist, 0.1)
        val = 4 / dist
        val *= translucencyMul

        #print("Calculated value for LED %i (%i, %i) to (%i, %i) Distance: %i; val: %f" % (led, LED[0], LED[1], x, y, dist, val))
        return max(0.0, min(1.0, val))
