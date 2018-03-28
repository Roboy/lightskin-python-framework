from typing import Callable, List

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