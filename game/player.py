from .card import Card


class Player:
    def __init__(self,player_id: int):
        self.id: int = player_id
        self.cards: list[Card] = []
        self.tricks: list[tuple[Card, ...]] = []

    def remove_card(self, card: Card) -> Card:
        self.cards.remove(card)
        return card

    def draw_card(self, card: Card) -> None:
        self.cards.append(card)

    def draw_cards(self, cards: list[Card]) -> None:
        self.cards.extend(cards)

    def win_trick(self, trick: tuple[Card, ...]) -> None:
        self.tricks.append(trick)

    def __str__(self) -> str:
        return f"Player({self.cards})"

    def __repr__(self) -> str:
        return self.__str__()
