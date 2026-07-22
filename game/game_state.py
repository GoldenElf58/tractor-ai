from asyncio import InvalidStateError
from random import shuffle

from .bid import Bid
from .card import Card
from .effective_suit import EffectiveSuit
from .face_suit import FaceSuit
from .move import Move
from .phase import Phase
from .play import Play
from .player import Player
from .trump_info import TrumpInfo


def generate_deck() -> list[Card]:
    deck: list[Card] = []
    for suit in (FaceSuit.SPADES, FaceSuit.DIAMONDS, FaceSuit.HEARTS, FaceSuit.CLUBS):
        for value in range(2, 15):
            deck.append(Card(suit, value, 1))
            deck.append(Card(suit, value, 2))
    for i in range(2):
        deck.append(Card(FaceSuit.JOKER, 16, i + 1))
        deck.append(Card(FaceSuit.JOKER, 17, i + 1))
    shuffle(deck)
    return deck


def get_trick_points(trick: tuple[Play, ...]) -> int:
    return sum(sum(get_card_points(card) for card in play.cards) for play in trick)


def get_card_points(card: Card) -> int:
    if card.rank == 5: return 5
    if card.rank == 10 or card.rank == 13: return 10
    return 0


def get_card(item: Card | Play | Bid | Move) -> Card | None:
    if isinstance(item, Card): return item
    if isinstance(item, Play): return item.cards[0]
    if isinstance(item, Bid): return item.card
    if isinstance(item, Move): return item.get_card()
    raise ValueError("Invalid item")


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
        self.last_trick: list[Play] = []
        self.trump_suit: FaceSuit = FaceSuit.JOKER
        self.phase: Phase = Phase.DRAWING
        self.offense_points: int = 0
        self.defense_points: int = 0
        self.trump_info: TrumpInfo | None = None
        self.setup_round()

    def setup_round(self) -> None:
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
        self.defense_points: int = 0

    def is_in_progress(self) -> bool:
        return self.phase != Phase.GAME_END

    def get_active_player(self) -> Player:
        return self.players[self.active_player]

    def show_current_hand(self) -> str:
        return self.get_active_player().show_hand()

    def show_current_trick(self) -> str:
        return ', '.join(map(str, self.curr_trick))

    def generate_moves(self) -> list[Move]:
        if self.phase == Phase.DRAWING:
            return [Move(bid) for bid in self.generate_bid_moves()]
        elif self.phase == Phase.BURYING:
            return [Move(card) for card in self.generate_bury_moves()]
        elif self.phase == Phase.TRICK_TAKING:
            return [Move(play) for play in self.generate_trick_moves()]
        return []

    def move(self, move: Move):
        if self.phase == Phase.DRAWING:
            if not isinstance(move.move, Bid): raise ValueError("Not a bid")
            self.move_bid(move.move)
        elif self.phase == Phase.BURYING:
            if isinstance(move.move, Card):
                self.move_bury(move.move)
            elif not isinstance(move.move, list):
                raise ValueError("Not a bury move")
            else:
                for card in move.move:
                    if not isinstance(card, Card): raise ValueError("Not a bury move")
                    self.move_bury(card)
        elif self.phase == Phase.TRICK_TAKING:
            if not isinstance(move.move, Play): raise ValueError("Not a trick-taking move")
            self.move_trick(move.move)
        elif self.phase == Phase.TRANSITION_ROUNDS:
            self.transition_rounds(self.active_player)
        else:
            raise RuntimeError("Not in valid phase")

    def generate_bury_moves(self) -> list[Card]:
        if self.phase != Phase.BURYING: raise RuntimeError("Not in burying phase")
        return self.get_active_player().cards

    def move_bury(self, card: Card) -> None:
        if self.phase != Phase.BURYING: raise RuntimeError("Not in burying phase")
        if self.active_player != self.round_leader:
            raise InvalidStateError("Active player should be the round leader")
        if card not in self.get_active_player().cards: raise ValueError("Invalid move")
        self.get_active_player().remove_card(card)
        self.trash.append(card)
        if (len(self.get_active_player().cards) ==
                len(self.players[(self.active_player + 1) % 4].cards)):
            self.phase = Phase.TRICK_TAKING
            self.trick_leader = self.active_player = self.round_leader

    def generate_bid_candidates(self) -> list[Card]:
        cards: list[Card] = self.get_active_player().cards
        return [card for card in cards if
                card.rank == self.dominant_rank or card.suit == FaceSuit.JOKER]

    def higher_bid(self, bid: Bid) -> bool:
        if bid.empty_bid: return False
        if bid.quantity < self.bid.quantity: return False
        if bid.quantity > self.bid.quantity: return True
        assert bid.card is not None and self.bid.card is not None
        return (bid.card.suit == FaceSuit.JOKER and
                (self.bid.card.suit != FaceSuit.JOKER or self.bid.card.rank < bid.card.rank))

    def generate_bid_moves(self) -> list[Bid]:
        if self.phase != Phase.DRAWING: raise RuntimeError("Not in drawing phase")
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
            valid_bid: bool = (
                    self.higher_bid(bid_candidate) and (not leader or card == self.bid.card) and
                    (bid_candidate.card.suit != FaceSuit.JOKER or bid_candidate.quantity == 2))
            if valid_bid:
                moves.append(bid_candidate)
        return moves

    def move_bid(self, move: Bid) -> None:
        if self.phase != Phase.DRAWING: raise RuntimeError("Not in drawing phase")
        if move.owner != self.active_player:
            print(repr(move))
            raise ValueError(f"Invalid owner. Got {move.owner} instead of {self.active_player}")
        moves: list[Bid] = self.generate_bid_moves()
        if move not in moves: raise ValueError("Invalid move")
        self.active_player = (self.active_player + 1) % self.num_players
        if self.active_player == self.round_leader and len(self.deck) <= 8:
            self.phase = Phase.BURYING
            self.get_active_player().draw_cards(self.deck)
            self.deck.clear()
            assert self.bid.card is not None if not self.bid.empty_bid else True
            self.trump_suit = FaceSuit.JOKER if self.bid.empty_bid else self.bid.card.suit
            self.trump_info = TrumpInfo(self.trump_suit, self.dominant_rank)
            for player in self.players:
                player.sort_hand(self.trump_suit, self.dominant_rank)
        else:
            self.get_active_player().draw_card(self.deck.pop(), self.dominant_rank)
        if move.empty_bid: return
        if not self.higher_bid(move): raise ValueError("Not higher bid")
        self.bid = move

    def generate_trick_leads(self) -> list[Play]:
        if self.phase != Phase.TRICK_TAKING: raise RuntimeError("Not in trick-taking phase")
        plays: list[Play] = []
        for card in self.get_active_player().cards:
            play: Play = Play([card], self.active_player)
            if play in plays:
                plays.append(Play([card.with_other_version(), card], self.active_player))
            plays.append(play)
        pair_plays: list[Play] = self.sorted(self.filtered(plays, 2))
        for i, play_1 in enumerate(pair_plays):
            for j, play_2 in enumerate(pair_plays):
                if j <= i: continue
                cards: list[Card] = []
                for play in pair_plays[i: j + 1]:
                    cards.extend(play.cards)
                play: Play = Play(cards, self.active_player)
                if play.is_consecutive_double(self.trump_info):
                    plays.append(play)
                else:
                    break
        return plays

    def filtered(self, plays: list[Play], quantity: int, suit: EffectiveSuit | None = None,
                 match_suit: int = -1, max_quantity: int = -1) -> list[Play]:
        if match_suit == -1:
            match_suit = quantity
        if max_quantity == -1:
            max_quantity = quantity
        filtered_plays: list[Play] = [
            play for play in plays
            if quantity <= play.quantity <= max_quantity and
               (suit is None or match_suit ==
                sum(play.cards[i].as_effective(self.trump_info) == suit for i in range(quantity)))
        ]
        return filtered_plays

    def sorted(self, cards: list[Card | Play | Bid | Move]) -> list:
        cards = sorted(cards, key=lambda item: card.rank if (card := get_card(
            item)) is not None and card.rank != self.dominant_rank else 15)
        cards = sorted(cards,
                       key=lambda item: 0 if (card := get_card(item)) is None else
                       card.as_effective(self.trump_info).value
                       + (2 if card.rank > 15 else 1 if
                       card.rank == self.dominant_rank and card.suit == self.trump_suit else 0))
        return cards

    def get_card_possibilities(self, rem_pairs: int, rem_suited: int, rem_any: int,
                               suit: EffectiveSuit) -> list[list[Card]]:
        if rem_pairs == 0 and rem_suited == 0 and rem_any == 0: return [[]]
        if rem_pairs:
            plays: list[Play] = self.filtered(self.generate_trick_leads(), 2, suit)
            card_plays: list[list[Card]] = [play.cards for play in plays]
        else:
            card_plays: list[list[Card]] = [
                [card] for card in self.get_active_player().cards
                if rem_suited == 0 or card.as_effective(self.trump_info) == suit]
            # card_plays: list[list[Card]] = [
            # [card] for card in self.get_active_player().card_plays] \
            #     if rem_suited == 0 else \
            #     [[card] for card in self.get_active_player().card_plays
            #      if card.as_effective(self.trump_info) == suit]
        child_possibilities: list[list[Card]] = \
            self.get_card_possibilities(max(0, rem_pairs - 1),
                                        max(0, rem_suited - 1) if rem_pairs == 0 else rem_suited,
                                        rem_any - 1 if rem_pairs == 0 and rem_suited == 0 else
                                        rem_any, suit)
        possibilities: list[list[Card]] = []
        for cards in card_plays:
            for possibility in child_possibilities:
                if any(any(card.exact_card(prev_card) for card in cards) for prev_card in
                       possibility):
                    continue
                possibilities.append([*possibility, *cards])
        return possibilities

    def generate_trick_moves(self) -> list[Play]:
        if self.phase != Phase.TRICK_TAKING: raise RuntimeError("Not in trick-taking phase")
        all_plays: list[Play] = self.generate_trick_leads()
        if len(self.curr_trick) == 0: return all_plays

        quantity: int = self.curr_trick[0].quantity
        suit: EffectiveSuit = self.curr_trick[0].cards[0].as_effective(self.trump_info)
        candidate_plays = self.filtered(all_plays, quantity, suit)
        if len(candidate_plays) == 0:
            if quantity == 1: return self.filtered(all_plays, 1)
            plays: list[Play] = []
            num_matching_led_suit: int = len(self.filtered(all_plays, 1, suit))
            consecutive_doubles: list[Play] = self.filtered(all_plays, 2, suit,
                                                            max_quantity=quantity)
            max_len: int = 0 if len(consecutive_doubles) == 0 else \
                max(len(play.cards) for play in consecutive_doubles)
            consecutive_doubles = [play for play in consecutive_doubles if play.quantity == max_len]
            if max_len == quantity: return consecutive_doubles
            rem_quantity: int = quantity - max_len
            rem_pairs: int = min(rem_quantity,
                                 len(self.filtered(all_plays, 2, suit)) - max_len // 2)
            rem_suited: int = min(rem_quantity - rem_pairs * 2,
                                  num_matching_led_suit - max_len - rem_pairs)
            rem_any: int = rem_quantity - rem_pairs * 2 - rem_suited
            rem_card_possibilities: list[list[Card]] = self.get_card_possibilities(rem_pairs,
                                                                                   rem_suited,
                                                                                   rem_any, suit)
            if len(consecutive_doubles) == 0:
                return [Play(cards, self.active_player) for cards in rem_card_possibilities]
            for play in consecutive_doubles:
                for rem_cards in rem_card_possibilities:
                    if any(any(card.exact_card(rem_card) for rem_card in rem_cards) for card in
                           play.cards):
                        continue
                    consec_double_cards = play.cards.copy()
                    consec_double_cards.extend(rem_cards)
                    plays.append(Play(consec_double_cards, self.active_player))
            return plays
        return candidate_plays

    def determine_trick_winner(self) -> int:
        lead_suit: EffectiveSuit = \
            self.curr_trick[0].cards[0].get_effective_suit(self.trump_suit, self.dominant_rank)
        best_card_index: int = 0
        best_play: Play = self.curr_trick[best_card_index]
        for i, play in enumerate(self.curr_trick):
            if not best_play.is_not_less(play, self.trump_info, lead_suit):
                best_card_index = i
                best_play = play
        return (best_card_index + self.trick_leader) % self.num_players

    def move_trick(self, play: Play):
        if self.phase != Phase.TRICK_TAKING: raise RuntimeError("Not in trick taking phase")
        moves: list[Play] = self.generate_trick_moves()
        if play not in moves: raise ValueError("Invalid move")
        for card in play.cards:
            self.get_active_player().remove_card(card)
        self.curr_trick.append(play)
        self.active_player = (self.active_player + 1) % self.num_players
        if len(self.curr_trick) == self.num_players:
            self.trick_leader = self.active_player = self.determine_trick_winner()
            self.get_active_player().win_trick(tuple(self.curr_trick))
            if len(self.players[0].cards) == 0:
                self.phase = Phase.TRANSITION_ROUNDS
                self.last_trick = self.curr_trick
            self.curr_trick = []

    def get_next_round_leader(self):
        return (self.round_leader + 2) % 4 if self.offense_points < 80 else \
            (self.round_leader + 1) % 4

    def get_next_team_levels(self) -> list[int]:
        self.score_points(self.active_player)
        next_levels: list[int] = self.team_levels.copy()
        next_round_leader: int = self.get_next_round_leader()
        if self.offense_points < 80:
            if next_levels[next_round_leader % 2] == 14:
                next_levels[next_round_leader % 2] = 15
                return next_levels
            if self.offense_points == 0:
                next_levels[next_round_leader % 2] += 3
            elif self.offense_points < 40:
                next_levels[next_round_leader % 2] += 2
            else:
                next_levels[next_round_leader % 2] += 1
            if self.defense_points >= 200:
                next_levels[next_round_leader % 2] += 1
        else:
            if self.offense_points < 120:
                pass
            elif self.offense_points < 160:
                next_levels[next_round_leader % 2] += 1
            elif self.offense_points < 200:
                next_levels[next_round_leader % 2] += 2
            else:
                next_levels[next_round_leader % 2] += 3
        next_levels[next_round_leader % 2] = min(next_levels[next_round_leader % 2], 14)
        return next_levels

    def get_next_dominant_rank(self):
        return self.get_next_team_levels()[self.get_next_round_leader() % 2]

    def transition_rounds(self, trick_winner: int):
        self.score_points(trick_winner)
        self.phase = Phase.DRAWING
        self.team_levels = self.get_next_team_levels()
        self.round_leader = self.get_next_round_leader()
        self.dominant_rank = self.team_levels[self.round_leader % 2]
        if self.dominant_rank == 15:
            self.phase = Phase.GAME_END
            return
        self.setup_round()

    def score_points(self, trick_winner: int = -1):
        player_a: int = (self.round_leader + 1) % 4
        player_b: int = (self.round_leader + 3) % 4
        player_c: int = (self.round_leader + 0) % 4
        player_d: int = (self.round_leader + 2) % 4
        self.offense_points = sum(
            get_trick_points(trick) for trick in (*self.players[player_a].tricks,
                                                  *self.players[player_b].tricks))
        self.defense_points = sum(
            get_trick_points(trick) for trick in (*self.players[player_c].tricks,
                                                  *self.players[player_d].tricks))
        if (self.phase == Phase.TRANSITION_ROUNDS and
                (trick_winner == player_a or trick_winner == player_b)):
            self.offense_points += sum(get_card_points(card) for card in self.trash) * \
                                   self.last_trick[0].quantity * 2

    def set_player_names(self, names: list[str]):
        for i, name in enumerate(names):
            self.players[i].name = name

    def get_player_name(self, player_id: int):
        if player_id < 0 or player_id > len(self.players): raise ValueError("Invalid player ID")
        return self.players[player_id].name

    def get_active_player_name(self) -> str:
        return self.get_player_name(self.active_player)

    def get_winning_team(self) -> int:
        if self.phase != Phase.GAME_END: raise ValueError("Game not over yet")
        return self.round_leader % 2
