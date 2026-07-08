from dataclasses import dataclass

from .face_suit import FaceSuit


@dataclass
class TrumpInfo:
    trump_suit: FaceSuit
    dominant_rank: int
