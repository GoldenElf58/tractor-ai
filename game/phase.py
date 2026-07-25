from enum import Enum


class Phase(Enum):
    DRAWING = 1
    BURYING = 2
    TRICK_TAKING = 3
    TRANSITION_ROUNDS = 4
    GAME_END = 5

    def __str__(self) -> str:
        match self:
            case Phase.DRAWING:
                return "Drawing Phase"
            case Phase.BURYING:
                return "Burying Phase"
            case Phase.TRICK_TAKING:
                return "Trick Taking Phase"
            case Phase.TRANSITION_ROUNDS:
                return "Transition Rounds"
            case Phase.GAME_END:
                return "Game Complete"
