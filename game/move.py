from dataclasses import dataclass

from .bid import Bid
from .card import Card
from .effective_suit import EffectiveSuit
from .face_suit import FaceSuit
from .phase import Phase
from .play import Play
from .trump_info import TrumpInfo


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

    def get_cards(self) -> list[Card]:
        if isinstance(self.move, Card): return [self.move]
        if isinstance(self.move, Play): return self.move.cards
        if isinstance(self.move, Bid): return [self.move.card] if self.move.card is not None else []
        if isinstance(self.move, list): return self.move
        return []

    def get_suits(self, trump_info: TrumpInfo | None) -> list[FaceSuit | EffectiveSuit]:
        suits: list[FaceSuit | EffectiveSuit] = []
        if isinstance(self.move, Bid):
            if self.move.card is not None:
                suits.append(self.move.card.suit)
        elif isinstance(self.move, Card):
            suits.append(self.move.as_effective(trump_info))
        elif isinstance(self.move, Play) or isinstance(self.move, list):
            for card in self.move if isinstance(self.move, list) else self.move.cards:
                suit: EffectiveSuit = card.as_effective(trump_info)
                if suit not in suits:
                    suits.append(suit)
        return suits

    def semi_sorted(self, cards: list[Card] | None = None) -> list[Card] | None:
        if cards is None:
            if isinstance(self.move, Play):
                cards = self.move.cards
            elif isinstance(self.move, list):
                cards = self.move
            else:
                return None
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
