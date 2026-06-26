from enum import Enum, auto

class Suit(Enum):
    SPADE = auto()
    HEART = auto()
    DIAMOND = auto()
    CLUB = auto()
    JOKER = auto()

    def __str__(self) -> str:
        match self:
            case Suit.SPADE:
                return "Spades"
            case Suit.HEART:
                return "Hearts"
            case Suit.DIAMOND:
                return "Diamond"
            case Suit.CLUB:
                return "Clubs"
            case Suit.JOKER:
                return "Joker"
