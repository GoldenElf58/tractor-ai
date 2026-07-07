from ease_function import EaseFunction


def int_to_word(n: int) -> str:
    match n:
        case 2:
            return "Pair"
        case 3:
            return "Triplet"
        case 4:
            return "Quadruplet"
        case _:
            return str(n)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class EaseOutCubic(EaseFunction):
    def __call__(self, start: float, end: float, t: float) -> float:
        return lerp(start, end, 1 - pow(1 - t, 3))

    def inverse(self, start: float, end: float, value: float) -> float:
        y = (value - start) / (end - start)
        return 1 - (1 - y) ** (1 / 3)


ease_out_cubic: EaseOutCubic = EaseOutCubic()
