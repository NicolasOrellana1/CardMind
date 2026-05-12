from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Suit(str, Enum):
    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"


RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")


@dataclass(frozen=True, slots=True)
class Card:
    rank: str
    suit: Suit

    @property
    def hard_value(self) -> int:
        if self.rank == "A":
            return 11
        if self.rank in {"J", "Q", "K"}:
            return 10
        return int(self.rank)

    @property
    def hi_lo_value(self) -> int:
        if self.rank in {"2", "3", "4", "5", "6"}:
            return 1
        if self.rank in {"10", "J", "Q", "K", "A"}:
            return -1
        return 0

    @property
    def label(self) -> str:
        symbols = {
            Suit.CLUBS: "C",
            Suit.DIAMONDS: "D",
            Suit.HEARTS: "H",
            Suit.SPADES: "S",
        }
        return f"{self.rank}{symbols[self.suit]}"


def standard_deck() -> list[Card]:
    return [Card(rank, suit) for suit in Suit for rank in RANKS]

