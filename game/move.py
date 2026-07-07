from dataclasses import dataclass

from game.bid import Bid
from game.card import Card
from game.phase import Phase
from game.play import Play


@dataclass
class Move:
    move: Bid | Card | Play | list[Card]
    type: Phase

    def __init__(self, move: Bid | Card | Play | list[Card]):
        self.move = move
        self.type = Phase.DRAWING if isinstance(move, Bid) else Phase.TRICK_TAKING \
            if isinstance(move, Play) else Phase.BURYING

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
                return cards[0] == self.move.card and self.move.quantity == 1
            return (((cards[0] == self.move.card and cards[1] == self.move.card_2) or
                     (cards[0] == self.move.card_2 and cards[1] == self.move.card)) and
                    self.move.quantity == len(cards))
        return False

    def __contains__(self, item):
        if isinstance(self.move, Card):
            return self.move.exact_card(item)
        if isinstance(self.move, Bid):
            return self.move.card is not None and self.move.card.exact_card(item)
        if isinstance(self.move, Play):
            return (self.move.card.exact_card(item) or
                    (self.move.card_2 and self.move.card_2.exact_card(item)))
        return False

    def __str__(self) -> str:
        return str(self.move)

    def __repr__(self) -> str:
        return repr(self.move)
