import random
import threading
import time

from typing_extensions import override

from game import GameState, Move
from game.bot import Bot


class Bot1(Bot):
    move: Move
    is_calculating: threading.Event = threading.Event()
    calculated: threading.Event = threading.Event()
    stop_calculation_signal: threading.Event = threading.Event()
    state_lock: threading.Lock = threading.Lock()

    @override
    def calculate_move_async(self, game_state: GameState) -> None:
        if self.is_calculating.is_set() or self.is_move_calculated(): return
        self.calculated.clear()
        self.is_calculating.set()
        threading.Thread(target=self.calculate_move, args=[game_state], daemon=True).start()

    @override
    def stop_calculating(self) -> None:
        if self.is_calculating.is_set():
            self.stop_calculation_signal.set()

    @override
    def calculate_move(self, game_state: GameState) -> None:
        time.sleep(1)
        moves: list[Move] = game_state.generate_moves()
        self.move = moves[random.randint(0, len(moves) - 1)]
        with self.state_lock:
            self.is_calculating.clear()
            if self.stop_calculation_signal.is_set():
                self.stop_calculation_signal.clear()
                return
            self.calculated.set()

    @override
    def is_move_calculated(self) -> bool:
        return self.calculated.is_set()

    @override
    def get_move(self) -> Move:
        if self.is_move_calculated():
            self.calculated.clear()
            return self.move
        raise RuntimeError("Move has not been calculated yet")
