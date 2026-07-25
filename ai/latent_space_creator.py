from typing import override

import torch
from torch import nn, Tensor

from ai.model import Model
from game import GameState, Card, FaceSuit, EffectiveSuit


def card_to_idx(card: Card) -> int:
    if card.suit == FaceSuit.JOKER:
        return (4 * 13 + (card.rank - 16)) * 2 + card.version - 1
    return ((int(card.suit) - 1) * 13 + (card.rank - 2)) * 2 + card.version - 1


def idx_to_card(idx: int) -> Card:
    if idx > 8 * 13 - 1:
        return Card(FaceSuit.JOKER, ((idx // 2) - 4 * 13) + 16, idx % 2 + 1)
    return Card(FaceSuit((idx // 2) // 13 + 1), (idx // 2) % 13 + 2, idx % 2 + 1)


def game_state_as_tensor(game_state: GameState, player_id: int) -> Tensor:
    """
    0 - not seen
    1 - in hand
    2 - in trash (if leader)
    3 - AI played previously
    4 - partner played previously
    5 - oponent a played previously
    6 - oponent b played previously
    7 - partner played this trick
    8 - opponent a played this trick
    9 - opponent b played this trick

    0 - 0-26+ - hand size (normalized)
    1 - 0-108 - cards remaining in draw pile (normalized)
    2-5 - one-hot - AI id
    6-9 - one-hot - round leader
    10-13 - one-hot - trick leader
    14-19 - one-hot encoding - lead suit (5 effective suits + none)
    20 - 2-14 - dominant rank (normalized)
    21 - 2-14 - team one level (normalized)
    22 - 2-14 - team two level (normalized)
    23 - 0-200+ - offense points (normalized)
    24 - 0-200+ - defense points (normalized)
    25-27 - one-hot encoding - game phase (drawing, burying, trick-taking)
    28-32 - one-hot - suits partner followed off-suit in
    33-37 - one-hot - suits opponent a followed off-suit in
    38-42 - one-hot - suits opponent b followed off-suit in
    """
    assert player_id == game_state.get_active_player().id
    card_tensor: Tensor = Tensor([[0.0] * 10] * 108)
    info_tensor: Tensor = Tensor([0.0] * 43)
    for i, card in enumerate(game_state.deck):
        card_idx: int = card_to_idx(card)
        card_tensor[card_idx][0] = 1

    for card in game_state.trash:
        card_idx: int = card_to_idx(card)
        if player_id == game_state.round_leader:
            card_tensor[card_idx][2] = 1
        else:
            card_tensor[card_idx][1] = 1

    for player in game_state.players:
        for card in player.cards:
            card_idx: int = card_to_idx(card)
            card_tensor[card_idx][1 if player.id == player_id else 0] = 1
        for trick in player.tricks:
            lead_suit: EffectiveSuit = trick[0].cards[0].suit
            for play in trick:
                for card in play.cards:
                    card_idx: int = card_to_idx(card)
                    card_info_idx: int
                    offsuit: bool = card.as_effective(game_state.trump_info) != lead_suit
                    if player.id == player_id:  # self
                        card_info_idx = 3
                    elif player.id == (player_id + 2) % 4:  # partner
                        card_info_idx = 4
                        if offsuit:
                            info_tensor[32 + lead_suit.value - 1] = 1
                    elif player.id == (player_id + 1) % 4:  # opponent 1
                        card_info_idx = 5
                        if offsuit:
                            info_tensor[37 + lead_suit.value - 1] = 1
                    elif player.id == (player_id + 3) % 4:  # opponent 2
                        card_info_idx = 6
                        if offsuit:
                            info_tensor[42 + lead_suit.value - 1] = 1
                    else:
                        raise ValueError(f"Invalid player id: {player.id}")
                    card_tensor[card_idx][card_info_idx] = 1

    for play in game_state.curr_trick:
        for card in play.cards:
            card_idx: int = card_to_idx(card)
            card_info_idx: int
            if play.owner == (player_id + 2) % 4:  # partner
                card_info_idx = 7
            elif play.owner == (player_id + 1) % 4:  # opponent 1
                card_info_idx = 8
            elif play.owner == (player_id + 3) % 4:  # opponent 2
                card_info_idx = 9
            else:
                raise ValueError(
                    f"AI (id {play.owner}) can't already have played a card this trick")
            card_tensor[card_idx][card_info_idx] = 1

    info_tensor[0] = len(game_state.get_active_player().cards) / 26.0
    info_tensor[1] = len(game_state.deck) / 108.0
    info_tensor[2 + player_id] = 1
    info_tensor[6 + game_state.round_leader] = 1
    info_tensor[10 + game_state.trick_leader] = 1
    if len(game_state.curr_trick) > 0:
        lead_suit = game_state.curr_trick[0].cards[0].as_effective(game_state.trump_info)
        info_tensor[15 + lead_suit.value - 1] = 1
    else:
        info_tensor[14] = 1
    info_tensor[20] = game_state.dominant_rank / 14.0
    info_tensor[21] = game_state.team_levels[0] / 14.0
    info_tensor[22] = game_state.team_levels[1] / 14.0
    info_tensor[23] = game_state.offense_points / 200.0
    info_tensor[24] = game_state.defense_points / 200.0
    if game_state.phase.value > 3:
        raise ValueError(f"Invalid phase: {game_state.phase}")
    info_tensor[25 + game_state.phase.value - 1] = 1

    card_tensor = card_tensor.flatten()
    return torch.concat([card_tensor, info_tensor])


class LatentSpaceCreator(Model):
    def __init__(self):
        layers = nn.Sequential(
            nn.Linear(1123, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        super().__init__(layers)

    @override
    def forward(self, x):
        if isinstance(x, GameState):
            x = game_state_as_tensor(x, x.get_active_player().id)
        # if x.ndim == 1:
        #     x = x.unsqueeze(0)
        return self.layers(x)
