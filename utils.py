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


def ease_out_cubic(a: float, b: float, t: float) -> float:
    return lerp(a, b, 1 - pow(1 - t, 3))


def ease_out_cubic_inverse(a: float, b: float, x: float) -> float:
    y = (x - a) / (b - a)
    return 1 - (1 - y) ** (1 / 3)


ease_out_cubic.inverse = ease_out_cubic_inverse
