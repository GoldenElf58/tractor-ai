from .suit import Suit


class Card:
    def __init__(self, suit: Suit, value: int):
        self.suit: Suit = suit
        self.value: int = value

    def greater_card(self, other: "Card", trump_rank: int, trump_suit: Suit, lead_suit: Suit) -> "Card":
        card: Card = self if self.is_not_less(other, trump_rank, trump_suit, lead_suit) else other
        assert card == self._greater_card(other, trump_rank, trump_suit, lead_suit)
        return card

    def _greater_card(self, other: "Card", trump_rank: int, trump_suit: Suit, lead_suit: Suit) -> "Card":
        if self.suit == Suit.JOKER: return self if other.suit != Suit.JOKER or other.value <= self.value else other
        if self.value == trump_rank: return self if other.value != trump_rank or other.suit != trump_suit else other
        if self.suit == trump_suit and other.suit != trump_suit: return self
        if self.suit != trump_suit and other.suit == trump_suit: return other
        if lead_suit == self.suit and other.suit != lead_suit: return self
        if lead_suit == other.suit and self.suit != lead_suit: return other
        return self if self.value >= other.value else other

    def is_not_less(self, other: "Card", trump_rank: int, trump_suit: Suit, lead_suit: Suit) -> bool:
        if self.suit == Suit.JOKER: return other.suit != Suit.JOKER or other.value <= self.value
        if self.value == trump_rank: return other.value != trump_rank or other.suit != trump_suit
        if self.suit == trump_suit and other.suit != trump_suit: return True
        if self.suit != trump_suit and other.suit == trump_suit: return False
        if lead_suit == self.suit and other.suit != lead_suit: return True
        if lead_suit == other.suit and self.suit != lead_suit: return False
        return self.value >= other.value

    def __str__(self) -> str:
        if self.suit == Suit.JOKER: return "Little Joker" if self.value == 1 else "Big Joker"
        if self.value == 11: return f"Jack of {self.suit}"
        if self.value == 12: return f"Queen of {self.suit}"
        if self.value == 13: return f"King of {self.suit}"
        if self.value == 14: return f"Ace of {self.suit}"
        return f"{self.value} of {self.suit}"

    def __repr__(self) -> str:
        return self.__str__()
