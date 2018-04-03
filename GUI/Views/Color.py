
class Color:

    def __init__(self, r: int, g: int, b: int):
        self.R = min(255, max(0, r))
        self.G = min(255, max(0, g))
        self.B = min(255, max(0, b))

    @classmethod
    def fromFloats(cls, r: float, g: float, b: float) -> 'Color':
        return cls(int(r * 255), int(g * 255), int(b * 255))

    def toHex(self) -> str:
        return "#%02x%02x%02x" % (self.R, self.G, self.B)
