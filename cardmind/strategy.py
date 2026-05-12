from __future__ import annotations

from dataclasses import dataclass

from .actions import Action
from .cards import Card
from .hand import Hand


def dealer_value(card: Card) -> int:
    return 11 if card.rank == "A" else min(card.hard_value, 10)


@dataclass(frozen=True)
class Advice:
    action: Action
    reason: str
    true_count: float
    running_count: int | None = None
    bet_units: int | None = None


@dataclass
class StrategyAdvisor:
    min_bet: int = 1
    max_bet: int = 12

    def advise(self, hand: Hand, dealer_upcard: Card, true_count: float = 0.0) -> Advice:
        base = self.basic_strategy(hand, dealer_upcard)
        action, reason = self.apply_count_deviation(hand, dealer_upcard, true_count, base)
        return Advice(action=action, reason=reason, true_count=true_count)

    def bet_units(self, true_count: float) -> int:
        if true_count < 1:
            return self.min_bet
        ramp = 1 + int(true_count * 2)
        return max(self.min_bet, min(self.max_bet, ramp))

    def basic_strategy(self, hand: Hand, dealer_upcard: Card) -> Action:
        up = dealer_value(dealer_upcard)

        if hand.can_split:
            pair_value = Hand.card_value(hand.cards[0])
            if pair_value in {8, 11}:
                return Action.SPLIT
            if pair_value == 10:
                return Action.STAND
            if pair_value == 9:
                return Action.SPLIT if up in {2, 3, 4, 5, 6, 8, 9} else Action.STAND
            if pair_value == 7:
                return Action.SPLIT if up <= 7 else Action.HIT
            if pair_value == 6:
                return Action.SPLIT if 2 <= up <= 6 else Action.HIT
            if pair_value == 5:
                return Action.DOUBLE if 2 <= up <= 9 else Action.HIT
            if pair_value == 4:
                return Action.SPLIT if up in {5, 6} else Action.HIT
            if pair_value in {2, 3}:
                return Action.SPLIT if 2 <= up <= 7 else Action.HIT

        if hand.is_soft and len(hand.cards) == 2:
            other = hand.total - 11
            if other >= 8:
                return Action.STAND
            if other == 7:
                if 3 <= up <= 6:
                    return Action.DOUBLE
                return Action.STAND if up in {2, 7, 8} else Action.HIT
            if other == 6:
                return Action.DOUBLE if 3 <= up <= 6 else Action.HIT
            if other in {4, 5}:
                return Action.DOUBLE if 4 <= up <= 6 else Action.HIT
            if other in {2, 3}:
                return Action.DOUBLE if 5 <= up <= 6 else Action.HIT

        total = hand.total
        if total >= 17:
            return Action.STAND
        if 13 <= total <= 16:
            return Action.STAND if 2 <= up <= 6 else Action.HIT
        if total == 12:
            return Action.STAND if 4 <= up <= 6 else Action.HIT
        if total == 11:
            return Action.DOUBLE
        if total == 10:
            return Action.DOUBLE if 2 <= up <= 9 else Action.HIT
        if total == 9:
            return Action.DOUBLE if 3 <= up <= 6 else Action.HIT
        return Action.HIT

    def apply_count_deviation(
        self,
        hand: Hand,
        dealer_upcard: Card,
        true_count: float,
        base: Action,
    ) -> tuple[Action, str]:
        up = dealer_value(dealer_upcard)
        total = hand.total
        hard = not hand.is_soft

        deviations: list[tuple[bool, Action, str]] = [
            (hard and total == 16 and up == 10 and true_count >= 0, Action.STAND, "Illustrious 18: stand on 16 vs 10 at TC >= 0."),
            (hard and total == 15 and up == 10 and true_count >= 4, Action.STAND, "Illustrious 18: stand on 15 vs 10 at TC >= +4."),
            (hard and total == 10 and up == 10 and true_count >= 4, Action.DOUBLE, "Index play: double 10 vs 10 at TC >= +4."),
            (hard and total == 10 and up == 11 and true_count >= 4, Action.DOUBLE, "Index play: double 10 vs A at TC >= +4."),
            (hard and total == 12 and up == 3 and true_count >= 2, Action.STAND, "Illustrious 18: stand on 12 vs 3 at TC >= +2."),
            (hard and total == 12 and up == 2 and true_count >= 3, Action.STAND, "Illustrious 18: stand on 12 vs 2 at TC >= +3."),
            (hard and total == 11 and up == 11 and true_count >= 1, Action.DOUBLE, "Illustrious 18: double 11 vs A at TC >= +1."),
            (hard and total == 9 and up == 2 and true_count >= 1, Action.DOUBLE, "Illustrious 18: double 9 vs 2 at TC >= +1."),
            (hard and total == 10 and up == 11 and true_count >= 4, Action.DOUBLE, "Illustrious 18: double 10 vs A at TC >= +4."),
            (hard and total == 13 and up == 2 and true_count < -1, Action.HIT, "Negative count deviation: hit 13 vs 2 below TC -1."),
            (hard and total == 12 and up == 4 and true_count < 0, Action.HIT, "Negative count deviation: hit 12 vs 4 below TC 0."),
        ]

        for applies, action, reason in deviations:
            if applies:
                return action, reason

        return base, "Basic strategy for this rule set."

    def policy(self, hand: Hand, dealer_upcard: Card, legal: set[Action], true_count: float) -> Action:
        action = self.advise(hand, dealer_upcard, true_count).action
        if action in legal:
            return action
        if action == Action.DOUBLE and Action.HIT in legal:
            return Action.HIT
        if action == Action.SPLIT and Action.HIT in legal:
            return Action.HIT
        return Action.STAND if Action.STAND in legal else next(iter(legal))

