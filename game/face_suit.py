from enum import Enum, auto

from game.effective_suit import EffectiveSuit


class FaceSuit(Enum):
    SPADE = auto()
    HEART = auto()
    DIAMOND = auto()
    CLUB = auto()
    JOKER = auto()

    def as_effective(self) -> EffectiveSuit:
        match self:
            case FaceSuit.SPADE:
                return EffectiveSuit.SPADE
            case FaceSuit.CLUB:
                return EffectiveSuit.CLUB
            case FaceSuit.HEART:
                return EffectiveSuit.HEART
            case FaceSuit.DIAMOND:
                return EffectiveSuit.DIAMOND
            case FaceSuit.JOKER:
                return EffectiveSuit.TRUMP

    def __str__(self) -> str:
        match self:
            case FaceSuit.SPADE:
                return "Spades"
            case FaceSuit.HEART:
                return "Hearts"
            case FaceSuit.DIAMOND:
                return "Diamonds"
            case FaceSuit.CLUB:
                return "Clubs"
            case FaceSuit.JOKER:
                return "Joker"

    def __repr__(self) -> str:
        return f"Suit.{self.__str__()}"
