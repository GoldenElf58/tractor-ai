from enum import Enum, auto


class Phase(Enum):
    DRAWING = auto()
    BURYING = auto()
    TRICK_TAKING = auto()
    GAME_END = auto()

    def __str__(self) -> str:
        match self:
            case Phase.DRAWING:
                return "Drawing Phase"
            case Phase.BURYING:
                return "Burying Phase"
            case Phase.TRICK_TAKING:
                return "Trick Taking Phase"
            case Phase.GAME_END:
                return "Game Complete"
