from dataclasses import dataclass

from game import Card
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

    def __str__(self) -> str:
        if self.quantity == 1:
            return self.cards[0].__str__()
        if self.quantity == 2:
            return f"{self.cards[0]} and {self.cards[1]}" if self.cards[0] != self.cards[1] else \
                f"{int_to_word(self.quantity)} of {self.cards[0]}"
        return ' and '.join(map(str, self.cards))
