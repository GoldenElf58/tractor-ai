from .card import Card


class Player:
    def __init__(self, cards: list[Card]):
        self.cards: list[Card] = cards

    def __str__(self) -> str:
        return f"Player({self.cards})"

    def __repr__(self) -> str:
        return self.__str__()