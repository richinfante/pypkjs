__author__ = 'katharine'

import PyV8 as v8
from console import Console
from performance import Performance
from timers import Timers


class PebbleKitJS(v8.JSClass):
    def __init__(self, loop):
        self.console = Console()
        self.performance = Performance()

        timerImpl = Timers(loop)
        self.setTimeout = lambda x, y: timerImpl.setTimeout(x, y)
        self.clearTimeout = lambda x: timerImpl.clearTimeout(x)
        self.setInterval = lambda x, y: timerImpl.setInterval(x, y)
        self.clearInterval = lambda x: timerImpl.clearInterval(x)
