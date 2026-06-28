from dataclasses import dataclass

from game import Card


@dataclass
class Play:
    card: Card
    quantity: int
    owner: int
