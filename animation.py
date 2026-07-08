from dataclasses import dataclass

from pygame.math import clamp

from ease_function import EaseFunction


@dataclass
class Animation:
    current: float
    start: float
    end: float
    time: float
    ease: EaseFunction

    def update(self, delta_time: float) -> None:
        self.time += delta_time
        self.time = clamp(self.time, 0, 1)
        self.current = self.ease(self.start, self.end, self.time)

    def set_bounds(self, start: float, end: float) -> None:
        self.start = start
        self.end = end
        self.current = clamp(self.current, min(self.start, self.end), max(self.start, self.end))
        self.time = self.ease.inverse(self.start, self.end, self.current)
