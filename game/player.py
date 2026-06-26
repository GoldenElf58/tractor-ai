from .card import Card


class Player:
    def __init__(self, cards: list[Card], player_id: int):
        self.cards: list[Card] = cards
        self.id: int = player_id
        self.tricks: list[tuple[Card, ...]] = []

    def play_card(self, card: Card) -> Card:
        self.cards.remove(card)
        return card

    def win_trick(self, trick: tuple[Card, ...]) -> None:
        self.tricks.append(trick)

    def __str__(self) -> str:
        return f"Player({self.cards})"

    def __repr__(self) -> str:
        return self.__str__()