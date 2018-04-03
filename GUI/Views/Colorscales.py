from typing import Callable, TypeVar

from GUI.Views.Color import Color

M = TypeVar('M')


def Grayscale(tofloat: Callable[[M], float]) -> Callable[[M], Color]:
    def display(val: M) -> Color:
        v = tofloat(val)
        return Color.fromFloats(v, v, v)

    return display
