from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .move import Move

if TYPE_CHECKING:
    from .game_state import GameState


class Bot(ABC):
    @abstractmethod
    def calculate_move_async(self, game_state: GameState) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop_calculating(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def calculate_move(self, game_state: GameState) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_move_calculated(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_move(self) -> Move:
        raise NotImplementedError
