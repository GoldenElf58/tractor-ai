from dataclasses import dataclass

from .bid import Bid
from .card import Card
from .phase import Phase
from .play import Play


@dataclass
class Move:
    move: Bid | Card | Play | list[Card]
    type: Phase

    def __init__(self, move: Bid | Card | Play | list[Card]):
        self.move = move
        self.type = Phase.DRAWING if isinstance(move, Bid) else Phase.TRICK_TAKING \
            if isinstance(move, Play) else Phase.BURYING

    def get_card(self) -> Card | None:
        if isinstance(self.move, Card): return self.move
        if isinstance(self.move, Play): return self.move.cards[0]
        if isinstance(self.move, Bid): return self.move.card
        if isinstance(self.move, list): return self.move[0]
        return None

    def semi_sorted(self, cards: list[Card] | None = None) -> list[Card] | None:
        if cards is None:
            if isinstance(self.move, Play):
                cards = self.move.cards
            else:
                cards = self.move
        if not isinstance(cards, list): return None
        cards = sorted(cards, key=lambda card: card.version)
        cards = sorted(cards, key=lambda card: card.rank)
        cards = sorted(cards, key=lambda card: card.suit.value)
        return cards

    def cards_match(self, cards: list[Card]):
        if len(cards) == 0:
            return isinstance(self.move, Bid) and self.move.empty_bid is None
        if isinstance(self.move, Card):
            return len(cards) == 1 and self.move == cards[0]
        if isinstance(self.move, list):
            return (len(cards) == len(self.move)
                    and all(card == self.move[i] for i, card in enumerate(cards)))
        if isinstance(self.move, Bid):
            return (len(cards) == self.move.quantity and
                    all(card == self.move.card for card in cards))
        if isinstance(self.move, Play):
            if len(cards) == 1:
                return cards[0] == self.move.cards[0] and self.move.quantity == 1
            if not (self.move.quantity == len(cards) >= 2): return False
            self_semi_sorted = self.semi_sorted()
            cards_semi_sorted = self.semi_sorted(cards)
            if self_semi_sorted is None or cards_semi_sorted is None: return False
            return all(self_card == other_card for self_card, other_card in
                       zip(self_semi_sorted, cards_semi_sorted))
        return False

    def __contains__(self, item):
        if isinstance(self.move, Card):
            return self.move.exact_card(item)
        if isinstance(self.move, Bid):
            return self.move.card is not None and self.move.card == item
        if isinstance(self.move, Play):
            return any(move.exact_card(item) for move in self.move.cards)
        return False

    def __str__(self) -> str:
        return str(self.move)

    def __repr__(self) -> str:
        return repr(self.move)
