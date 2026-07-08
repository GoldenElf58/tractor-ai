from .face_suit import FaceSuit
from .play import Play
from .card import Card


class Player:
    def __init__(self, player_id: int):
        self.id: int = player_id
        self.cards: list[Card] = []
        self.tricks: list[tuple[Play, ...]] = []

    def remove_card(self, card: Card) -> Card:
        self.cards.remove(card)
        return card

    def draw_card(self, card: Card, dominant_rank: int = 1) -> None:
        self.cards.append(card)
        self.sort_hand(FaceSuit.JOKER, dominant_rank)

    def sort_hand(self, trump_suit: FaceSuit, dominant_rank: int):
        self.cards.sort(key=lambda card: card.rank if card.rank != dominant_rank else 15)
        self.cards.sort(key=lambda card: card.get_effective_suit(trump_suit, dominant_rank).value
                                         + (2 if card.rank > 15 else 1
        if card.rank == dominant_rank and card.suit == trump_suit else 0))

    def show_hand(self) -> str:
        return ', '.join(map(str, self.cards))

    def draw_cards(self, cards: list[Card]) -> None:
        self.cards.extend(cards)
        self.sort_hand(FaceSuit.JOKER, 1)

    def win_trick(self, trick: tuple[Play, ...]) -> None:
        self.tricks.append(trick)

    def __str__(self) -> str:
        return f"Player({self.cards})"

    def __repr__(self) -> str:
        return self.__str__()
