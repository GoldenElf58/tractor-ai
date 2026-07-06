from enum import Enum

from game.effective_suit import EffectiveSuit


class FaceSuit(Enum):
    DIAMONDS = 1
    CLUBS = 2
    HEARTS = 3
    SPADES = 4
    JOKER = 5

    def as_effective(self) -> EffectiveSuit:
        match self:
            case FaceSuit.SPADES:
                return EffectiveSuit.SPADES
            case FaceSuit.CLUBS:
                return EffectiveSuit.CLUBS
            case FaceSuit.HEARTS:
                return EffectiveSuit.HEARTS
            case FaceSuit.DIAMONDS:
                return EffectiveSuit.DIAMONDS
            case FaceSuit.JOKER:
                return EffectiveSuit.TRUMP

    def __str__(self) -> str:
        match self:
            case FaceSuit.SPADES:
                return "Spades"
            case FaceSuit.HEARTS:
                return "Hearts"
            case FaceSuit.DIAMONDS:
                return "Diamonds"
            case FaceSuit.CLUBS:
                return "Clubs"
            case FaceSuit.JOKER:
                return "Joker"

    def __repr__(self) -> str:
        return f"Suit.{self.__str__()}"
