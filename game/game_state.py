from random import shuffle

from .card import Card
from .player import Player
from .suit import Suit


def generate_deck() -> list[Card]:
    deck: list[Card] = []
    for suit in (Suit.SPADE, Suit.DIAMOND, Suit.HEART, Suit.CLUB):
        for value in range(2, 15):
            deck.append(Card(suit, value))
            deck.append(Card(suit, value))
    for i in range(2):
        deck.append(Card(Suit.JOKER, 1))
        deck.append(Card(Suit.JOKER, 2))
    shuffle(deck)
    return deck


class GameState:
    def __init__(self):
        self.num_players: int = 4
        self.deck: list[Card] = generate_deck()
        self.players = self.generate_players()
        self.player_turn: int = 0
        self.trick_leader: int = 0
        self.curr_trick: list[Card] = []
        self.trump_rank: int = 2
        self.trump_suit: Suit = Suit.SPADE

    def generate_players(self) -> list[Player]:
        players: list[Player] = []
        for i in range(self.num_players):
            start = i * 25
            stop = start + 25
            players.append(Player(self.deck[start:stop], i))
        return players

    def get_active_player_id(self) -> int:
        return self.player_turn

    def generate_moves(self) -> list[Card]:
        if len(self.curr_trick) == 0:
            return self.players[self.get_active_player_id()].cards
        candidate_cards: list[Card] = [card for card in self.players[self.get_active_player_id()].cards if
                                       card.suit == self.curr_trick[0].suit]
        if len(candidate_cards) == 0:
            return self.players[self.get_active_player_id()].cards
        return candidate_cards

    def determine_trick_winner(self) -> int:
        lead_suit: Suit = self.curr_trick[0].suit
        best_card: Card = self.curr_trick[0]
        best_card_index: int = 0
        for i, card in enumerate(self.curr_trick):
            if not best_card.is_not_less(card, self.trump_rank, self.trump_suit, lead_suit):
                best_card_index = i
                best_card = card
        return (best_card_index + self.trick_leader) % self.num_players

    def move(self, card: Card):
        moves: list[Card] = self.generate_moves()
        if card not in moves: raise ValueError("Invalid move")
        self.curr_trick.append(self.players[self.get_active_player_id()].play_card(card))
        self.player_turn = (self.player_turn + 1) % self.num_players
        if len(self.curr_trick) == self.num_players:
            self.player_turn = self.determine_trick_winner()
            self.players[self.player_turn].win_trick(tuple(self.curr_trick))
            self.curr_trick = []
