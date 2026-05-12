from __future__ import annotations

import random
from dataclasses import dataclass, field

from .cards import Card, standard_deck


@dataclass
class Shoe:
    decks: int = 6
    penetration: float = 0.75
    rng: random.Random = field(default_factory=random.Random)
    cards: list[Card] = field(default_factory=list)
    running_count: int = 0
    dealt_cards: int = 0

    def __post_init__(self) -> None:
        self.shuffle()

    def shuffle(self) -> None:
        self.cards = standard_deck() * self.decks
        self.rng.shuffle(self.cards)
        self.running_count = 0
        self.dealt_cards = 0

    @property
    def total_cards(self) -> int:
        return 52 * self.decks

    @property
    def penetration_cards(self) -> int:
        return int(self.total_cards * self.penetration)

    @property
    def cards_remaining(self) -> int:
        return len(self.cards)

    @property
    def decks_remaining(self) -> float:
        return max(self.cards_remaining / 52, 0.25)

    @property
    def true_count(self) -> float:
        return self.running_count / self.decks_remaining

    def needs_shuffle(self) -> bool:
        return self.dealt_cards >= self.penetration_cards or len(self.cards) < 20

    def draw(self) -> Card:
        if not self.cards:
            self.shuffle()
        card = self.cards.pop()
        self.running_count += card.hi_lo_value
        self.dealt_cards += 1
        return card

