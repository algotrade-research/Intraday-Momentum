import pandas as pd
from enum import Enum

class TimeStatus(Enum):
    PREPARE = 1
    COLLECT = 2
    TRADE = 3
    END = 4

class Signal(Enum):
    LONG = 1
    SHORT = 2