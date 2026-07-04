from enum import Enum, auto


class Phase(Enum):
    DRAWING = auto()
    BURYING = auto()
    TRICK_TAKING = auto()
    GAME_END = auto()
