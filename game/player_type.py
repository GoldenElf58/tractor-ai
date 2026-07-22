from enum import Enum, auto

class PlayerType(Enum):
    HUMAN = auto()
    BOT = auto()

    def __str__(self) -> str:
        return "Human" if self == PlayerType.HUMAN else "Bot"
