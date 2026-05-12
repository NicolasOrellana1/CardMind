from __future__ import annotations

import random
from dataclasses import dataclass, field

from .actions import Action
from .cards import Card
from .hand import Hand
from .shoe import Shoe


@dataclass(frozen=True)
class GameConfig:
    decks: int = 6
    penetration: float = 0.75
    blackjack_payout: float = 1.5
    dealer_hits_soft_17: bool = False
    double_after_split: bool = True
    surrender_allowed: bool = True
    max_splits: int = 3


@dataclass
class RoundResult:
    player_hands: list[Hand]
    dealer_hand: Hand
    payouts: list[float]
    running_count: int
    true_count: float

    @property
    def net(self) -> float:
        return sum(self.payouts)


@dataclass
class BlackjackGame:
    config: GameConfig = field(default_factory=GameConfig)
    seed: int | None = None

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.shoe = Shoe(self.config.decks, self.config.penetration, self.rng)

    def start_round(self, bet: float = 1.0) -> tuple[list[Hand], Hand]:
        if self.shoe.needs_shuffle():
            self.shoe.shuffle()
        player = Hand(bet=bet)
        dealer = Hand()
        player.add(self.shoe.draw())
        dealer.add(self.shoe.draw())
        player.add(self.shoe.draw())
        dealer.add(self.shoe.draw())
        return [player], dealer

    def legal_actions(self, hand: Hand, dealer_upcard: Card, split_count: int = 0) -> set[Action]:
        if hand.resolved or hand.is_bust or hand.is_surrendered:
            return set()

        actions = {Action.HIT, Action.STAND}
        first_decision = len(hand.cards) == 2
        if first_decision:
            actions.add(Action.DOUBLE)
            if self.config.surrender_allowed and not hand.is_split_hand:
                actions.add(Action.SURRENDER)
            if dealer_upcard.rank == "A":
                actions.add(Action.INSURANCE)
        if (
            hand.can_split
            and first_decision
            and split_count < self.config.max_splits
            and (self.config.double_after_split or not hand.is_split_hand)
        ):
            actions.add(Action.SPLIT)
        return actions

    def play_hand(
        self,
        hand: Hand,
        dealer: Hand,
        policy,
        split_count: int = 0,
    ) -> list[Hand]:
        completed: list[Hand] = []
        while not hand.resolved and not hand.is_bust and not hand.is_surrendered:
            legal = self.legal_actions(hand, dealer.cards[0], split_count)
            if not legal:
                break
            action = policy(hand, dealer.cards[0], legal, self.shoe.true_count)
            if action not in legal:
                action = Action.STAND

            if action == Action.HIT:
                hand.add(self.shoe.draw())
            elif action == Action.STAND:
                hand.resolved = True
            elif action == Action.DOUBLE:
                hand.bet *= 2
                hand.is_doubled = True
                hand.add(self.shoe.draw())
                hand.resolved = True
            elif action == Action.SURRENDER:
                hand.is_surrendered = True
                hand.resolved = True
            elif action == Action.SPLIT:
                first, second = hand.cards
                left = Hand(cards=[first], bet=hand.bet, is_split_hand=True)
                right = Hand(cards=[second], bet=hand.bet, is_split_hand=True)
                left.add(self.shoe.draw())
                right.add(self.shoe.draw())
                completed.extend(self.play_hand(left, dealer, policy, split_count + 1))
                completed.extend(self.play_hand(right, dealer, policy, split_count + 1))
                return completed
            elif action == Action.INSURANCE:
                hand.resolved = True
        completed.append(hand)
        return completed

    def dealer_play(self, dealer: Hand) -> None:
        while True:
            if dealer.total < 17:
                dealer.add(self.shoe.draw())
                continue
            if dealer.total == 17 and dealer.is_soft and self.config.dealer_hits_soft_17:
                dealer.add(self.shoe.draw())
                continue
            break

    def settle(self, player_hands: list[Hand], dealer: Hand) -> list[float]:
        payouts: list[float] = []
        dealer_blackjack = dealer.is_blackjack

        for hand in player_hands:
            if hand.is_surrendered:
                payouts.append(-0.5 * hand.bet)
            elif hand.is_blackjack and not dealer_blackjack:
                payouts.append(self.config.blackjack_payout * hand.bet)
            elif dealer_blackjack and not hand.is_blackjack:
                payouts.append(-hand.bet)
            elif hand.is_bust:
                payouts.append(-hand.bet)
            elif dealer.is_bust:
                payouts.append(hand.bet)
            elif hand.total > dealer.total:
                payouts.append(hand.bet)
            elif hand.total < dealer.total:
                payouts.append(-hand.bet)
            else:
                payouts.append(0.0)
        return payouts

    def play_round(self, policy, bet: float = 1.0) -> RoundResult:
        player_hands, dealer = self.start_round(bet)

        if player_hands[0].is_blackjack or dealer.is_blackjack:
            payouts = self.settle(player_hands, dealer)
            return RoundResult(player_hands, dealer, payouts, self.shoe.running_count, self.shoe.true_count)

        completed: list[Hand] = []
        for hand in player_hands:
            completed.extend(self.play_hand(hand, dealer, policy))

        if any(not hand.is_bust and not hand.is_surrendered for hand in completed):
            self.dealer_play(dealer)

        payouts = self.settle(completed, dealer)
        return RoundResult(completed, dealer, payouts, self.shoe.running_count, self.shoe.true_count)

