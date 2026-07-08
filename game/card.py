from dataclasses import dataclass

from .effective_suit import EffectiveSuit
from .face_suit import FaceSuit
from .trump_info import TrumpInfo


@dataclass
class Card:
    suit: FaceSuit
    rank: int
    version: int

    def as_effective(self, trump_info: TrumpInfo | None) -> EffectiveSuit:
        return self.suit.as_effective() if (trump_info is None or self.suit != trump_info.trump_suit
                                            and self.rank != trump_info.dominant_rank) \
            else EffectiveSuit.TRUMP

    def get_effective_suit(self, trump_suit: FaceSuit, dominant_rank: int) -> EffectiveSuit:
        return self.suit.as_effective() if self.suit != trump_suit and self.rank != dominant_rank \
            else EffectiveSuit.TRUMP

    def greater_card(self, other: "Card", trump_rank: int, trump_suit: FaceSuit,
                     lead_suit: EffectiveSuit) -> "Card":
        card: Card = self if self.is_not_less(other, trump_rank, trump_suit, lead_suit) else other
        assert card == self._greater_card(other, trump_rank, trump_suit, lead_suit)
        return card

    def _greater_card(self, other: "Card", dominant_rank: int, trump_suit: FaceSuit,
                      lead_suit: EffectiveSuit) -> "Card":
        this_effective_suit: EffectiveSuit = self.get_effective_suit(trump_suit, dominant_rank)
        other_effective_suit: EffectiveSuit = other.get_effective_suit(trump_suit, dominant_rank)
        if self.suit == FaceSuit.JOKER:
            return self if other.suit != FaceSuit.JOKER or other.rank <= self.rank else other
        if self.rank == dominant_rank:
            return self if other.rank != dominant_rank or other.suit != trump_suit else other
        if self.suit == trump_suit and other.suit != trump_suit: return self
        if self.suit != trump_suit and other.suit == trump_suit: return other
        if lead_suit == this_effective_suit and other_effective_suit != lead_suit: return self
        if lead_suit == other_effective_suit and this_effective_suit != lead_suit: return other
        return self if self.rank >= other.rank else other

    def is_not_less(self, other: "Card", dominant_rank: int, trump_suit: FaceSuit,
                    lead_suit: EffectiveSuit) -> bool:
        this_effective_suit: EffectiveSuit = self.get_effective_suit(trump_suit, dominant_rank)
        other_effective_suit: EffectiveSuit = other.get_effective_suit(trump_suit, dominant_rank)
        if self.suit == FaceSuit.JOKER:
            return other.suit != FaceSuit.JOKER or other.rank <= self.rank
        if self.rank == dominant_rank:
            return other.rank != dominant_rank or other.suit != trump_suit
        if (this_effective_suit == EffectiveSuit.TRUMP and
                other_effective_suit != EffectiveSuit.TRUMP): return True
        if (this_effective_suit != EffectiveSuit.TRUMP and
                other_effective_suit == EffectiveSuit.TRUMP): return False
        if lead_suit == this_effective_suit and lead_suit != other_effective_suit: return True
        if lead_suit == other_effective_suit and this_effective_suit != lead_suit: return False
        return self.rank >= other.rank

    def get_filename(self):
        rank: str = self.rank.__str__()
        match self.rank:
            case 11:
                return f"jack_of_{self.suit.name.lower()}2.png"
            case 12:
                return f"queen_of_{self.suit.name.lower()}2.png"
            case 13:
                return f"king_of_{self.suit.name.lower()}2.png"
            case 14:
                return f"ace_of_{self.suit.name.lower()}.png"
            case 16 | 17:
                rank = "red" if self.rank == 17 else "black"
                return f"{rank}_joker.png"
        return f"{rank}_of_{self.suit.name.lower()}.png"

    def with_other_version(self):
        return Card(self.suit, self.rank, 2 if self.version == 1 else 1)

    def __hash__(self):
        return hash((self.suit, self.rank, self.version))

    def __str__(self) -> str:
        if self.suit == FaceSuit.JOKER: return "Little Joker" if self.rank == 16 else "Big Joker"
        if self.rank == 11: return f"Jack of {self.suit}"
        if self.rank == 12: return f"Queen of {self.suit}"
        if self.rank == 13: return f"King of {self.suit}"
        if self.rank == 14: return f"Ace of {self.suit}"
        return f"{self.rank} of {self.suit}"

    def __repr__(self) -> str:
        # return self.__str__()
        return f"Card(suit={self.suit}, rank={self.rank}, version={self.version})"

    def exact_card(self, other: object) -> bool:
        if not isinstance(other, Card): return False
        return self.rank == other.rank and self.suit == other.suit and self.version == other.version

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card): return False
        return self.rank == other.rank and self.suit == other.suit
