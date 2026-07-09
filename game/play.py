from dataclasses import dataclass

from . import FaceSuit, EffectiveSuit
from .card import Card, TrumpInfo
from utils import int_to_word


@dataclass
class Play:
    cards: list[Card]
    quantity: int
    owner: int

    def __init__(self, cards: list[Card], owner: int):
        self.cards = cards
        self.quantity = len(cards)
        self.owner = owner

    def is_pair(self) -> bool:
        return self.quantity == 2 and self.cards[0] == self.cards[1]

    def is_consecutive_double(self, trump_info: TrumpInfo | None) -> bool:
        if len(self.cards) % 2 == 1: return False
        for i, card in enumerate(self.cards):
            if i == len(self.cards) - 1: break
            if i % 2 == 1:
                if card.as_effective(trump_info) != self.cards[i + 1].as_effective(trump_info):
                    return False
                if not card.is_consecutive(self.cards[i + 1], trump_info): return False
                continue
            if card != self.cards[i + 1]: return False
        return True

    def is_not_less(self, other: Play, trump_info: TrumpInfo | None,
                    lead_suit: EffectiveSuit) -> bool:
        if trump_info is None:
            trump_info = TrumpInfo(FaceSuit.JOKER, 0)
        if self.quantity != other.quantity: return self.quantity > other.quantity
        if self.quantity == 1:
            return self.cards[0].is_not_less(other.cards[0], trump_info.dominant_rank,
                                             trump_info.trump_suit, lead_suit)
        if self.is_consecutive_double(trump_info) and other.is_consecutive_double(trump_info):
            return self.cards[0].is_not_less(other.cards[0], trump_info.dominant_rank,
                                             trump_info.trump_suit, lead_suit)
        if other.is_consecutive_double(trump_info):
            return False
        if self.is_consecutive_double(trump_info):
            return True
        return self.cards[0].is_not_less(other.cards[0], trump_info.dominant_rank,
                                         trump_info.trump_suit, lead_suit)

    def __str__(self) -> str:
        if self.quantity == 1:
            return self.cards[0].__str__()
        if self.quantity == 2:
            return f"{self.cards[0]} and {self.cards[1]}" if self.cards[0] != self.cards[1] else \
                f"{int_to_word(self.quantity)} of {self.cards[0]}"
        return ' and '.join(map(str, self.cards))
