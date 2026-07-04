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
        deck.append(Card(FaceSuit.JOKER, 16))
        deck.append(Card(FaceSuit.JOKER, 17))
    shuffle(deck)
    return deck


def get_trick_points(trick: tuple[Play, ...]) -> int:
    return sum(get_card_points(play.card) for play in trick)


def get_card_points(card: Card) -> int:
    if card.rank == 5: return 5
    if card.rank == 10 or card.rank == 13: return 10
    return 0


class GameState:
    def __init__(self):
        self.num_players: int = 4
        self.players = [Player(i) for i in range(self.num_players)]
        self.team_levels: list[int] = [2, 2]
        self.deck: list[Card] = generate_deck()
        self.trash: list[Card] = []
        self.bid = Bid(True, None, 0, -1)
        self.active_player: int = 0
        self.trick_leader: int = 0
        self.round_leader: int = 0
        self.dominant_rank: int = 2
        self.curr_trick: list[Play] = []
        self.trump_suit: FaceSuit = FaceSuit.JOKER
        self.phase: Phase = Phase.DRAWING
        self.offense_points: int = 0
        self.setup_game()

    def setup_game(self) -> None:
        self.deck = generate_deck()
        self.trash.clear()
        for player in self.players:
            player.tricks.clear()
            player.cards.clear()
        self.players[self.round_leader].draw_card(self.deck.pop())
        self.bid = Bid(True, None, 0, -1)
        self.active_player: int = self.round_leader
        self.trick_leader: int = self.round_leader
        self.dominant_rank: int = self.team_levels[self.round_leader % 2]
        self.curr_trick.clear()
        self.trump_suit: FaceSuit = FaceSuit.JOKER
        self.phase: Phase = Phase.DRAWING
        self.offense_points: int = 0

    def is_in_progress(self) -> bool:
        return self.phase != Phase.GAME_END

    def get_active_player(self) -> Player:
        return self.players[self.active_player]

    def show_current_hand(self) -> str:
        return self.get_active_player().show_hand(self.trump_suit, self.dominant_rank)

    def show_current_trick(self) -> str:
        return ', '.join(map(str, self.curr_trick))

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
            valid_bid: bool = (self.higher_bid(bid_candidate) and (not leader or card == self.bid.card) and
                               (bid_candidate.card.suit != FaceSuit.JOKER or bid_candidate.quantity == 2))
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
            self.trump_suit = FaceSuit.JOKER if self.bid.empty_bid else self.bid.card.suit
        else:
            self.get_active_player().draw_card(self.deck.pop())
        if move.empty_bid: return
        if not self.higher_bid(move): raise ValueError("Not higher bid")
        self.bid = move

    def generate_trick_moves(self) -> list[Play]:
        if self.phase != Phase.TRICK_TAKING: raise ValueError("Not in trick-taking phase")
        all_plays: list[Play] = []
        for card in self.get_active_player().cards:
            play: Play = Play(card, None, 1, self.active_player)
            if play not in all_plays:
                all_plays.append(play)
            else:
                all_plays.append(Play(card, card, 2, self.active_player))
        if len(self.curr_trick) == 0:
            return all_plays
        candidate_plays = [play for play in all_plays if play.card.suit == self.curr_trick[0].card.suit and
                           play.quantity == self.curr_trick[0].quantity]
        if len(candidate_plays) == 0:
            if self.curr_trick[0].quantity == 1: return all_plays
            plays: list[Play] = []
            num_matching_led_suit: int = sum(
                1 for card in self.get_active_player().cards if card.suit == self.curr_trick[0].card.suit)
            for i, card_1 in enumerate(self.get_active_player().cards):
                if num_matching_led_suit >= 1 and card_1.suit != self.curr_trick[0].card.suit: continue
                for j, card_2 in enumerate(self.get_active_player().cards):
                    if i >= j: continue
                    if num_matching_led_suit >= 2 and card_2.suit != self.curr_trick[0].card.suit: continue
                    play: Play = Play(card_1, card_2, 2, self.active_player)
                    plays.append(play)
            return plays
        return candidate_plays

    def determine_trick_winner(self) -> int:
        lead_suit: EffectiveSuit = self.curr_trick[0].card.get_effective_suit(self.trump_suit, self.dominant_rank)
        best_card: Card = self.curr_trick[0].card
        best_card_index: int = 0
        for i, play in enumerate(self.curr_trick):
            if self.curr_trick[0].quantity == 2 and play.card != play.card_2: continue
            if not best_card.is_not_less(play.card, self.dominant_rank, self.trump_suit, lead_suit):
                best_card_index = i
                best_card = play.card
        return (best_card_index + self.trick_leader) % self.num_players

    def move_trick(self, play: Play):
        if self.phase != Phase.TRICK_TAKING: raise ValueError("Not in trick taking phase")
        moves: list[Play] = self.generate_trick_moves()
        if play not in moves: raise ValueError("Invalid move")
        self.get_active_player().remove_card(play.card)
        if play.quantity == 2:
            self.get_active_player().remove_card(play.card_2)
        self.curr_trick.append(play)
        self.active_player = (self.active_player + 1) % self.num_players
        if len(self.curr_trick) == self.num_players:
            self.active_player = self.determine_trick_winner()
            self.get_active_player().win_trick(tuple(self.curr_trick))
            if len(self.players[0].cards) == 0:
                self.transition_rounds(self.active_player)
            self.curr_trick = []

    def transition_rounds(self, trick_winner: int):
        self.phase = Phase.DRAWING
        self.score_points(trick_winner)
        if self.offense_points < 80:
            self.round_leader = (self.round_leader + 2) % 4
            if self.team_levels[self.round_leader % 2] == 14:
                self.phase = Phase.GAME_END
                self.team_levels[self.round_leader % 2] = 15
                return
            if self.offense_points == 0:
                self.team_levels[self.round_leader % 2] += 3
            elif self.offense_points < 40:
                self.team_levels[self.round_leader % 2] += 2
            else:
                self.team_levels[self.round_leader % 2] += 1
        else:
            self.round_leader = (self.round_leader + 1) % 4
            if self.offense_points < 120:
                pass
            elif self.offense_points < 160:
                self.team_levels[self.round_leader % 2] += 1
            else:
                self.team_levels[self.round_leader % 2] += 2
        self.team_levels[self.round_leader % 2] = max(self.team_levels[self.round_leader % 2], 14)
        self.dominant_rank = self.team_levels[self.round_leader % 2]
        self.setup_game()

    def score_points(self, trick_winner: int):
        player_a: int = (self.round_leader + 1) % 4
        player_b: int = (self.round_leader + 3) % 4
        self.offense_points = sum(get_trick_points(trick) for trick in (*self.players[player_a].tricks,
                                                                        *self.players[player_b].tricks))
        if trick_winner == player_a or trick_winner == player_b:
            self.offense_points += sum(get_card_points(card) for card in self.trash) * self.curr_trick[0].quantity * 2
