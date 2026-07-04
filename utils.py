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
