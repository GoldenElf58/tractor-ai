from dataclasses import dataclass
from .card import Card


@dataclass
class Bid:
    empty_bid: bool
    card: Card | None
    quantity: int
    owner: int
