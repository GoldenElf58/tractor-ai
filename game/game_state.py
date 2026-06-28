from asyncio import InvalidStateError
from random import shuffle

from .bid import Bid
from .card import Card
from .effective_suit import EffectiveSuit
from .phase import Phase
from .play import Play
from .player import Player
from .face_suit import FaceSuit


def generate_deck() -> list[Card]:
    deck: list[Card] = []
    for suit in (FaceSuit.SPADE, FaceSuit.DIAMOND, FaceSuit.HEART, FaceSuit.CLUB):
        for value in range(2, 15):
            deck.append(Card(suit, value))
            deck.append(Card(suit, value))
    for i in range(2):
        deck.append(Card(FaceSuit.JOKER, 1))
        deck.append(Card(FaceSuit.JOKER, 2))
    shuffle(deck)
    return deck


class GameState:
    def __init__(self):
        self.num_players: int = 4
        self.deck: list[Card] = generate_deck()
        self.trash: list[Card] = []
        self.players = [Player(i) for i in range(self.num_players)]
        self.players[0].draw_card(self.deck.pop())
        self.bid = Bid(True, None, 0, -1)
        self.active_player: int = 0
        self.trick_leader: int = 0
        self.curr_trick: list[Card] = []
        self.dominant_rank: int = 2
        self.trump_suit: FaceSuit = FaceSuit.SPADE
        self.phase: Phase = Phase.DRAWING

    def get_active_player(self) -> Player:
        return self.players[self.active_player]

    def generate_moves(self) -> list[Bid | Card | Play]:
        if self.phase == Phase.DRAWING:
            return self.generate_bid_moves()
        elif self.phase == Phase.BURYING:
            return self.generate_bury_moves()
        elif self.phase == Phase.TRICK_TAKING:
            return self.generate_trick_moves()
        return []

    def move(self, move: Bid | Card | Play):
        if self.phase == Phase.DRAWING:
            if not isinstance(move, Bid): raise ValueError("Not a bid")
            self.move_bid(move)
        elif self.phase == Phase.BURYING:
            if not isinstance(move, Card): raise ValueError("Not a bury move")
            self.move_bury(move)
        elif self.phase == Phase.TRICK_TAKING:
            if not isinstance(move, Play): raise ValueError("Not a trick-taking move")
            self.move_trick(move)
        else:
            raise ValueError("Not in valid phase")

    def generate_bury_moves(self) -> list[Card]:
        if self.phase != Phase.BURYING: raise ValueError("Not in burying phase")
        if self.active_player != 0: raise InvalidStateError("Active player should be 0")
        return self.get_active_player().cards

    def move_bury(self, card: Card) -> None:
        if self.active_player != 0: raise InvalidStateError("Active player should be 0")
        if card not in self.get_active_player().cards: raise ValueError("Invalid move")
        self.get_active_player().remove_card(card)
        self.trash.append(card)
        if len(self.get_active_player().cards) == len(self.players[1].cards):
            self.phase = Phase.TRICK_TAKING
            self.active_player = self.trick_leader = self.bid.owner

    def generate_bid_candidates(self) -> list[Card]:
        cards: list[Card] = self.get_active_player().cards
        return [card for card in cards if card.rank == self.dominant_rank or card.suit == FaceSuit.JOKER]

    def higher_bid(self, bid: Bid) -> bool:
        if bid.empty_bid: return False
        if bid.quantity < self.bid.quantity: return False
        if bid.quantity > self.bid.quantity: return True
        return (bid.card.suit == FaceSuit.JOKER and
                (self.bid.card.suit != FaceSuit.JOKER or self.bid.card.rank < bid.card.rank))

    def generate_bid_moves(self) -> list[Bid]:
        if self.phase != Phase.DRAWING: raise ValueError("Not in drawing phase")
        bid_candidates: list[Card] = self.generate_bid_candidates()
        bid_candidates.sort(key=lambda candidate: candidate.rank)
        leader: bool = self.bid.owner == self.active_player
        moves: list[Bid] = [Bid(True, None, 0, self.active_player)]
        quantity = 1
        for i, card in enumerate(bid_candidates):
            if i > 0 and card == bid_candidates[i - 1]:
                quantity += 1
            else:
                quantity = 1
            bid_candidate: Bid = Bid(False, card, quantity, self.active_player)
            valid_bid: bool = self.higher_bid(bid_candidate) and (not leader or card == self.bid.card)
            if valid_bid:
                moves.append(bid_candidate)
        return moves

    def move_bid(self, move: Bid) -> None:
        if self.phase != Phase.DRAWING: raise ValueError("Not in drawing phase")
        if move.owner != self.active_player: raise ValueError("Not your turn")
        moves: list[Bid] = self.generate_bid_moves()
        if move not in moves: raise ValueError("Invalid move")
        self.active_player = (self.active_player + 1) % self.num_players
        if self.active_player == 0 and len(self.deck) <= 8:
            self.phase = Phase.BURYING
            self.get_active_player().draw_cards(self.deck)
            self.deck.clear()
            self.trump_suit = self.bid.card.suit
            self.dominant_rank = self.bid.card.rank
        else:
            self.get_active_player().draw_card(self.deck.pop())
        if move.empty_bid: return
        if not self.higher_bid(move): raise ValueError("Not higher bid")
        self.bid = move

    def generate_trick_moves(self) -> list[Play]:
        if self.phase != Phase.TRICK_TAKING: raise ValueError("Not in trick-taking phase")
        all_plays: list[Play] = []
        for card in self.get_active_player().cards:
            play: Play = Play(card, 1, self.active_player)
            if play not in all_plays:
                all_plays.append(play)
            else:
                all_plays.append(Play(card, 2, self.active_player))
        if len(self.curr_trick) == 0:
            return all_plays
        candidate_plays = [play for play in all_plays if play.card.suit == self.curr_trick[0].suit]
        if len(candidate_plays) == 0:
            return all_plays
        return candidate_plays

    def determine_trick_winner(self) -> int:
        lead_suit: EffectiveSuit = self.curr_trick[0].get_effective_suit(self.trump_suit, self.dominant_rank)
        best_card: Card = self.curr_trick[0]
        best_card_index: int = 0
        for i, card in enumerate(self.curr_trick):
            if not best_card.is_not_less(card, self.dominant_rank, self.trump_suit, lead_suit):
                best_card_index = i
                best_card = card
        return (best_card_index + self.trick_leader) % self.num_players

    def move_trick(self, play: Play):
        if self.phase != Phase.TRICK_TAKING: raise ValueError("Not in trick taking phase")
        moves: list[Play] = self.generate_trick_moves()
        if play not in moves: raise ValueError("Invalid move")
        for i in range(play.quantity):
            self.curr_trick.append(self.get_active_player().remove_card(play.card))
        self.active_player = (self.active_player + 1) % self.num_players
        if len(self.curr_trick) == self.num_players:
            self.active_player = self.determine_trick_winner()
            self.get_active_player().win_trick(tuple(self.curr_trick))
            self.curr_trick = []
