from typing import override

import torch
from torch import nn, Tensor
from torch.optim import Optimizer

from ai.card_decider import CardDecider
from ai.latent_space_creator import LatentSpaceCreator, card_to_idx
from ai.model import Model
from ai.structure_decider import StructureDecider
from ai.suit_decider import SuitDecider
from game import GameState, FaceSuit, EffectiveSuit, Phase, Play, Move, Bid


class FullModel(Model):
    def __init__(self):
        super().__init__(nn.Sequential(), create_optimizer=False)
        self.latent_space_creator = LatentSpaceCreator()
        self.structure_decider = StructureDecider()
        self.suit_decider = SuitDecider()
        self.card_decider = CardDecider()
        self.optimizer: Optimizer = torch.optim.Adam(self.parameters(), lr=0.01)

    def get_move(self, game_state: GameState) -> Move:
        output: Tensor = self(game_state)
        suit_num: int = int(torch.argmax(output[:6]).item()) + 1
        suit: FaceSuit | EffectiveSuit | None = None if suit_num == 6 else FaceSuit(suit_num) \
            if game_state.phase == Phase.DRAWING else EffectiveSuit(suit_num)
        structure_num: int = int(torch.argmax(output[6:9]).item())
        length: int = int(output[9])
        moves: list[Move] = game_state.generate_moves()
        filtered_moves: list[Move] = []
        for move in moves:
            move_len: int = len(move.get_cards())
            if structure_num == 0 and move_len != 1: continue  # TODO: Change if burying 8 at once
            if structure_num == 1 and move_len != length * 2: continue
            if structure_num == 2:
                if isinstance(move.move, Bid):
                    if move.move.card is None:
                        filtered_moves.append(move)
                    continue
                elif move_len // 2 != length:
                    continue

            suits: list[FaceSuit | EffectiveSuit] = move.get_suits(game_state.trump_info)
            move_suit_amount: int = len(suits)
            if move_suit_amount == 1:
                if suit is not None and suit.value == suits[0].value:
                    filtered_moves.append(move)
                continue
            if suit is not None: continue
            filtered_moves.append(move)

        if len(filtered_moves) == 0:
            raise RuntimeError("There should be at least one move available.")
        if len(filtered_moves) == 1:
            return filtered_moves[0]

        card_mask: Tensor = torch.zeros(108)
        for move in filtered_moves:
            for card in move.get_cards():
                card_mask[card_to_idx(card)] = 1
        card_probabilities: Tensor = output[10:]
        card_probabilities = torch.mul(card_probabilities, card_mask)
        move_probabilities = []
        for move in filtered_moves:
            move_probabilities.append(
                sum(card_probabilities[card_to_idx(card)] for card in move.get_cards()))
        selected_move = filtered_moves[torch.argmax(Tensor(move_probabilities))]
        return selected_move

    @override
    def forward(self, x: GameState):
        latent_space: Tensor = self.latent_space_creator(x)

        suit_output: Tensor = self.suit_decider(latent_space)
        valid_suits: Tensor = torch.zeros(6)
        for move in x.generate_moves():
            suits: list[FaceSuit | EffectiveSuit] = move.get_suits(x.trump_info)
            if len(suits) > 1:
                valid_suits[5] = 1  # Mix of suits or none (if bidding)
            for suit in suits:
                valid_suits[int(suit) - 1] = 1
        suit_output = torch.mul(suit_output, valid_suits)
        suit_refined: Tensor = torch.zeros(6)
        suit_refined[torch.argmax(suit_output)] = 1

        if x.phase == Phase.TRICK_TAKING:
            structure_input: Tensor = torch.concat([latent_space, suit_refined])
            structure_out: Tensor = self.structure_decider(structure_input)
            valid_structures: Tensor = torch.zeros(4)
            valid_lengths: list[int] = []
            for move in x.generate_moves():
                if isinstance(move.move, Play):
                    if len(move.move.cards) == 1:
                        valid_structures[0] = 1  # Single card
                    elif len(move.get_suits(x.trump_info)) == 1:
                        valid_structures[1] = 1  # Pair
                        valid_structures[3] = 1  # Pair length
                        valid_lengths.append(len(move.move.cards) // 2)
                    else:
                        valid_structures[2] = 1  # Mix or none if bidding
            structure_out = torch.mul(structure_out, valid_structures)
            length = round(structure_out[3].item())
            if length not in valid_lengths:
                length = 0 if len(valid_lengths) == 0 else max(valid_lengths)
            structure_refined: Tensor = Tensor([0, 0, 0, length])
            structure_refined[torch.argmax(structure_out[:3])] = 1
        elif x.phase == Phase.DRAWING:
            structure_input: Tensor = torch.concat([latent_space, suit_refined])
            structure_out: Tensor = self.structure_decider(structure_input)
            valid_structures: Tensor = torch.zeros(4)
            for move in x.generate_moves():
                if isinstance(move.move, Bid):
                    if move.move.quantity == 1:
                        valid_structures[0] = 1  # Single card
                    elif move.move.quantity == 2:
                        valid_structures[1] = 1  # Pair
                        valid_structures[3] = 1  # Pair length
                    else:
                        valid_structures[2] = 1  # Mix or none if bidding
            structure_out = torch.mul(structure_out, valid_structures)
            structure_refined: Tensor = torch.zeros(4)
            structure: int = int(torch.argmax(structure_out[:3]))
            if structure == 1 or structure == 2:
                structure_refined[3] = 1
            structure_refined[structure] = 1
        else:
            structure_refined = torch.zeros(4)  # TODO: Make it work for 8 cards at once?

        card_input: Tensor = torch.concat([latent_space, suit_refined, structure_refined])
        card_probabilities: Tensor = self.card_decider(card_input)
        return torch.concat([suit_refined, structure_refined, card_probabilities])
