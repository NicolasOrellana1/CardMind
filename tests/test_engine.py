import unittest

from cardmind.actions import Action
from cardmind.cards import Card, Suit
from cardmind.engine import BlackjackGame, GameConfig
from cardmind.hand import Hand
from cardmind.shoe import Shoe
from cardmind.strategy import StrategyAdvisor


def c(rank: str) -> Card:
    return Card(rank, Suit.SPADES)


class HandTests(unittest.TestCase):
    def test_soft_total_adjusts_when_busting(self):
        hand = Hand([c("A"), c("7"), c("9")])
        self.assertEqual(hand.total, 17)
        self.assertFalse(hand.is_soft)

    def test_blackjack_requires_two_cards_and_unsplit(self):
        self.assertTrue(Hand([c("A"), c("K")]).is_blackjack)
        self.assertFalse(Hand([c("A"), c("K")], is_split_hand=True).is_blackjack)

    def test_pairs_compare_ten_value_cards(self):
        self.assertTrue(Hand([c("K"), c("10")]).can_split)


class ShoeTests(unittest.TestCase):
    def test_hi_lo_running_count_updates_on_draw(self):
        shoe = Shoe(decks=1)
        shoe.cards = [c("K"), c("5")]
        shoe.running_count = 0
        shoe.dealt_cards = 0
        self.assertEqual(shoe.draw().rank, "5")
        self.assertEqual(shoe.running_count, 1)
        self.assertEqual(shoe.draw().rank, "K")
        self.assertEqual(shoe.running_count, 0)


class StrategyTests(unittest.TestCase):
    def test_basic_strategy_splits_aces_and_eights(self):
        advisor = StrategyAdvisor()
        self.assertEqual(advisor.basic_strategy(Hand([c("A"), c("A")]), c("6")), Action.SPLIT)
        self.assertEqual(advisor.basic_strategy(Hand([c("8"), c("8")]), c("10")), Action.SPLIT)

    def test_basic_strategy_stands_hard_16_against_6(self):
        advisor = StrategyAdvisor()
        self.assertEqual(advisor.basic_strategy(Hand([c("10"), c("6")]), c("6")), Action.STAND)

    def test_count_deviation_stands_16_vs_10_at_zero_or_better(self):
        advisor = StrategyAdvisor()
        advice = advisor.advise(Hand([c("10"), c("6")]), c("10"), true_count=0)
        self.assertEqual(advice.action, Action.STAND)

    def test_bet_ramp_is_capped(self):
        advisor = StrategyAdvisor(max_bet=8)
        self.assertEqual(advisor.bet_units(-2), 1)
        self.assertEqual(advisor.bet_units(100), 8)


class EngineTests(unittest.TestCase):
    def test_legal_actions_on_first_two_cards(self):
        game = BlackjackGame(GameConfig())
        hand = Hand([c("8"), c("8")])
        actions = game.legal_actions(hand, c("A"))
        self.assertIn(Action.HIT, actions)
        self.assertIn(Action.STAND, actions)
        self.assertIn(Action.DOUBLE, actions)
        self.assertIn(Action.SPLIT, actions)
        self.assertIn(Action.SURRENDER, actions)
        self.assertIn(Action.INSURANCE, actions)

    def test_settle_blackjack_pays_three_to_two(self):
        game = BlackjackGame(GameConfig())
        player = Hand([c("A"), c("K")], bet=10)
        dealer = Hand([c("10"), c("7")])
        self.assertEqual(game.settle([player], dealer), [15])

    def test_dealer_stands_on_soft_17_by_default(self):
        game = BlackjackGame(GameConfig(dealer_hits_soft_17=False), seed=1)
        dealer = Hand([c("A"), c("6")])
        game.dealer_play(dealer)
        self.assertEqual(len(dealer.cards), 2)

    def test_simulated_round_returns_result(self):
        game = BlackjackGame(seed=3)
        advisor = StrategyAdvisor()
        result = game.play_round(advisor.policy)
        self.assertGreaterEqual(len(result.player_hands), 1)
        self.assertEqual(len(result.payouts), len(result.player_hands))


if __name__ == "__main__":
    unittest.main()

