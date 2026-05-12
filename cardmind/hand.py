from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card


@dataclass
class Hand:
    cards: list[Card] = field(default_factory=list)
    bet: float = 1.0
    is_split_hand: bool = False
    is_doubled: bool = False
    is_surrendered: bool = False
    resolved: bool = False

    def add(self, card: Card) -> None:
        self.cards.append(card)

    @property
    def total(self) -> int:
        total = sum(card.hard_value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == "A")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_soft(self) -> bool:
        hard_total = sum(card.hard_value for card in self.cards)
        return any(card.rank == "A" for card in self.cards) and hard_total <= 21

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total == 21 and not self.is_split_hand

    @property
    def is_bust(self) -> bool:
        return self.total > 21

    @property
    def can_split(self) -> bool:
        return len(self.cards) == 2 and self.card_value(self.cards[0]) == self.card_value(self.cards[1])

    @property
    def is_pair(self) -> bool:
        return self.can_split

    @staticmethod
    def card_value(card: Card) -> int:
        return 11 if card.rank == "A" else min(card.hard_value, 10)

    def clone_without_flags(self) -> "Hand":
        return Hand(cards=list(self.cards), bet=self.bet)

    def labels(self) -> list[str]:
        return [card.label for card in self.cards]

