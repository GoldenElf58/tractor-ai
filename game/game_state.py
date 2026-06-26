from random import shuffle

from .card import Card
from .phase import Phase
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
        self.phase = Phase()

    def generate_players(self) -> list[Player]:
        players: list[Player] = []
        for i in range(self.num_players):
            start = i * 25
            stop = start + 25
            players.append(Player(self.deck[start:stop]))
        return players


