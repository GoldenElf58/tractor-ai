from dataclasses import dataclass

from utils import int_to_word
from .card import Card


@dataclass
class Bid:
    empty_bid: bool
    card: Card | None
    quantity: int
    owner: int

    def __str__(self) -> str:
        if self.empty_bid: return "Pass"
        if self.quantity == 1:
            return self.card.__str__()
        return f"{int_to_word(self.quantity)} of {self.card}"
