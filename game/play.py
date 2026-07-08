from dataclasses import dataclass

from game import Card
from utils import int_to_word


@dataclass
class Play:
    card: Card
    card_2: Card | None
    quantity: int
    owner: int

    def is_pair(self) -> bool:
        return self.card == self.card_2 and self.quantity == 2

    def __str__(self) -> str:
        if self.quantity == 1:
            return self.card.__str__()
        return f"{self.card} and {self.card_2}" if self.card != self.card_2 else \
            f"{int_to_word(self.quantity)} of {self.card}"
