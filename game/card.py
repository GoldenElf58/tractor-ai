from .suit import Suit


class Card:
    def __init__(self, suit: Suit, value: int):
        self.suit: Suit = suit
        self.value: int = value

    def __str__(self) -> str:
        if self.suit == Suit.JOKER:
            return "Little Joker" if self.value == 1 else "Big Joker"
        return f"{self.value} of {self.suit}"

    def __repr__(self) -> str:
        return self.__str__()