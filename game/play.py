from dataclasses import dataclass

from game import Card
from utils import int_to_word


@dataclass
class Play:
    card: Card
    card_2: Card | None
    quantity: int
    owner: int

    def __str__(self) -> str:
        if self.quantity == 1:
            return self.card.__str__()
        return f"{self.card} and {self.card_2}" if self.card_2 != self.card else\
            f"{int_to_word(self.quantity)} of {self.card}"

